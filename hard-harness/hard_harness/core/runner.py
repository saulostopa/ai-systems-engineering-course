"""Runner — ÚNICA autoridade de transição de estado.

Princípios (requisitos do curso):
  1. Agentes produzem propostas (NodeOutput.proposed_next); o runner DECIDE.
  2. Agente nunca altera status — tentativa vira Event de erro (auditável).
  3. Transições passam por gates; dados inválidos bloqueiam.
  4. Toda transição vira Event e checkpoint no store.
  5. Limites: MAX_DEPTH, MAX_CHILDREN, MAX_RETRIES, MAX_LLM_CALLS, timeout,
     orçamento de LLM opcional — aplicados EM CÓDIGO (ADK 2, L4b).
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable

from .events import Event, EventBus
from .graph import Node, WorkflowGraph
from .schemas import NodeInput, NodeOutput, NodeKind, WorkflowState, WorkflowStatus


@dataclass
class Limits:
    """Limites obrigatórios — aplicados pelo runner, não pelos agentes."""

    max_depth: int = 8
    max_children: int = 16
    max_retries: int = 3
    max_llm_calls: int = 40
    run_timeout_s: float = 1800.0
    llm_budget: float = 0.0  # 0 = sem orçamento; >0 = teto em unidades de custo


class Runner:
    """Executa o grafo. O único objeto que chama state transitions."""

    def __init__(
        self,
        graph: WorkflowGraph,
        store=None,            # StateStore (None = sem persistência)
        bus: EventBus | None = None,
        limits: Limits | None = None,
        node_dispatch: dict[str, Callable[[NodeInput], NodeOutput]] | None = None,
    ) -> None:
        self.graph = graph
        self.store = store
        self.bus = bus or EventBus()
        self.limits = limits or Limits()
        # dispatch extra (ex.: gates injetados) por id de nó
        self.node_dispatch = node_dispatch or {}
        self._started_at = 0.0
        self._llm_cost = 0.0

    # ── API pública ───────────────────────────────────────────────

    def run(self, initial: dict[str, Any] | None = None, state: WorkflowState | None = None) -> WorkflowState:
        """Executa do início (ou retoma de um estado salvo)."""
        self._started_at = time.monotonic()
        if state is None:
            state = WorkflowState(workflow_id=self._new_workflow_id(), data=initial or {})
            self._transition(state, WorkflowStatus.RUNNING, "init", "workflow iniciado")
            node_id = self.graph.start
        else:
            node_id = state.current_node  # retomada
        self._checkpoint(state)
        try:
            return self._advance_from(state, node_id, depth=0)
        except TimeoutError as exc:
            state.error = str(exc)
            self._transition(state, WorkflowStatus.FAILED, "runner", f"timeout: {exc}")
            self._checkpoint(state)
            return state
        except Exception as exc:  # falha inesperada: explícita e auditável
            state.error = f"{type(exc).__name__}: {exc}"
            self._transition(state, WorkflowStatus.FAILED, "runner", state.error)
            self._checkpoint(state)
            return state

    # ── Núcleo: avanço de estado (uso interno) ────────────────────

    def _advance_from(self, state: WorkflowState, node_id: str, depth: int) -> WorkflowState:
        if depth > self.limits.max_depth:
            raise RuntimeError(f"MAX_DEPTH excedido ({self.limits.max_depth})")
        if self._elapsed() > self.limits.run_timeout_s:
            raise TimeoutError(f"run_timeout_s excedido ({self.limits.run_timeout_s})")

        node = self.graph.nodes[node_id]
        state.current_node = node_id
        state.depth = max(state.depth, depth)
        self._transition(state, WorkflowStatus.RUNNING, node_id, f"entrando em {node_id}")

        output = self._execute_node(node, state, depth)

        # ── Autoridade de transição: proposta do agente ≠ transição ──
        if not output.ok:
            return self._handle_failure(state, node, output, depth)

        state.data[node_id] = output.payload
        state.llm_calls += 1 if node.kind is NodeKind.AGENT else 0
        self._check_llm_limits(state, node)

        # Gates anexados à saída (ex.: validação de plano) bloqueiam a transição
        if output.gate and not output.gate.passed:
            self.bus.emit(Event("gate", node_id, f"gate falhou: {output.gate.failures}", {"failures": output.gate.failures}))
            return self._handle_failure(state, node, output, depth)

        for ev in output.evidence:
            self.bus.emit(Event("evidence", node_id, f"evidência {ev.kind} {'PASS' if ev.passed else 'FAIL'}", {"evidence": ev.to_dict()}))

        self._checkpoint(state)

        # ── Fan-out nativo: nó com N sucessores dispara filhos em paralelo ──
        # (exceção: nós com router explícito — o router decide a rota única)
        successors = self.graph.edges.get(node_id, [])
        if len(successors) > 1 and node_id not in self.graph.routers:
            children = [self.graph.nodes[s] for s in successors if s in self.graph.nodes]
            aggregated = run_fanout(self, state, node_id, children)
            state.data[f"fanout_{node_id}"] = aggregated
            join_id = self._join_after(node_id, successors)
            if join_id is None:
                raise RuntimeError(f"fan-out de {node_id} sem JoinNode — transição não pode ser silenciosa")
            self._transition(state, WorkflowStatus.RUNNING, join_id, f"join após fan-out de {node_id}")
            self._checkpoint(state)
            return self._advance_from(state, join_id, depth + 1)

        next_node = self._next_node(state, node_id, output)
        if next_node is None:
            self._transition(state, WorkflowStatus.CLOSED, node_id, "workflow encerrado (fim do grafo)")
            self._checkpoint(state)
            return state
        return self._advance_from(state, next_node, depth + 1)

    def _execute_node(self, node: Node, state: WorkflowState, depth: int) -> NodeOutput:
        payload = state.data.get(node.id, {})
        ninput = NodeInput(node_id=node.id, state=state, payload=payload)
        fn = self.node_dispatch.get(node.id, node.fn)
        if node.timeout_s > 0:
            return self._run_with_timeout(fn, ninput, node.timeout_s)
        try:
            return fn(ninput)
        except Exception as exc:
            return NodeOutput(node_id=node.id, ok=False, error=f"{type(exc).__name__}: {exc}")

    @staticmethod
    def _run_with_timeout(fn: Callable[[NodeInput], NodeOutput], ninput: NodeInput, timeout_s: float) -> NodeOutput:
        import threading

        result: dict[str, Any] = {"output": None}

        def target() -> None:
            try:
                result["output"] = fn(ninput)
            except Exception as exc:
                result["error"] = f"{type(exc).__name__}: {exc}"

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout_s)
        if thread.is_alive():
            return NodeOutput(node_id=ninput.node_id, ok=False, error=f"timeout do nó ({timeout_s}s)")
        if result.get("error"):
            return NodeOutput(node_id=ninput.node_id, ok=False, error=result["error"])
        return result["output"]

    # ── Falhas, retries e roteamento ──────────────────────────────

    def _join_after(self, node_id: str, successors: list[str]) -> str | None:
        """Encontra o JoinNode cujas fontes são os sucessores do fan-out."""
        wanted = set(successors)
        for join_id, sources in self.graph.joins.items():
            if set(sources) == wanted:
                return join_id
        return None

    def _handle_failure(self, state: WorkflowState, node: Node, output: NodeOutput, depth: int) -> WorkflowState:
        state.retries[node.id] = state.retries.get(node.id, 0) + 1
        attempts = state.retries[node.id]
        self.bus.emit(Event("error", node.id, output.error or "falha do nó", {"attempts": attempts}))
        if attempts <= self.limits.max_retries:
            self._transition(state, WorkflowStatus.RUNNING, node.id, f"retry {attempts}/{self.limits.max_retries}")
            self._checkpoint(state)
            return self._advance_from(state, node.id, depth + 1)
        state.error = f"MAX_RETRIES excedido em {node.id} ({self.limits.max_retries})"
        self._transition(state, WorkflowStatus.FAILED, node.id, state.error)
        self._checkpoint(state)
        return state

    def _next_node(self, state: WorkflowState, node_id: str, output: NodeOutput) -> str | None:
        """Roteamento pós-nó:
        1. router explícito (default obrigatório);
        2. proposta de agente (runner decide — pode recusar);
        3. arestas sequenciais;
        4. None = fim."""
        if node_id in self.graph.routers:
            fn, routes, default = self.graph.routers[node_id]
            route = fn(state.data)
            dst = routes.get(route, default)
            self.bus.emit(Event("transition", node_id, f"router: {route} -> {dst}", {"route": route, "dst": dst}))
            return dst
        if output.proposed_next:
            dst = output.proposed_next
            if dst not in self.graph.nodes:
                self.bus.emit(Event("agent_proposal", node_id, f"proposta inválida ignorada: {dst}", {"proposed": dst}))
            elif dst not in self.graph.edges.get(node_id, []):
                self.bus.emit(Event("agent_proposal", node_id, f"proposta fora das arestas ignorada: {dst}", {"proposed": dst}))
            else:
                self.bus.emit(Event("agent_proposal", node_id, f"proposta aceita: {dst}", {"proposed": dst}))
                return dst
        succ = self.graph.edges.get(node_id, [])
        if len(succ) == 1:
            return succ[0]
        return None  # fan-out é tratado pelo nó de dispatch; join pelo próximo nó

    # ── Limites ──────────────────────────────────────────────────

    def _check_llm_limits(self, state: WorkflowState, node: Node) -> None:
        if state.llm_calls > self.limits.max_llm_calls:
            raise RuntimeError(f"MAX_LLM_CALLS excedido ({self.limits.max_llm_calls})")
        if self.limits.llm_budget > 0 and node.kind is NodeKind.AGENT:
            self._llm_cost += 1.0
            if self._llm_cost > self.limits.llm_budget:
                raise RuntimeError(f"llm_budget excedido ({self.limits.llm_budget})")

    def _elapsed(self) -> float:
        return time.monotonic() - self._started_at

    # ── Transições e persistência (só aqui!) ─────────────────────

    def _transition(self, state: WorkflowState, status: WorkflowStatus, node_id: str, message: str) -> None:
        """A ÚNICA função que muda o status. Nenhum agente/nó pode chamá-la."""
        state.status = status
        state.current_node = node_id
        state.updated_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        self.bus.emit(Event("transition", node_id, message, {"status": status.value}))

    def _checkpoint(self, state: WorkflowState) -> None:
        if self.store:
            self.store.write_state(state)

    @staticmethod
    def _new_workflow_id() -> str:
        import uuid

        return f"wf_{uuid.uuid4().hex[:12]}"


# ── Helper de fan-out paralelo (nós determinísticos) ───────────────

def run_fanout(runner: Runner, state: WorkflowState, parent_id: str, children: list[Node]) -> dict[str, dict[str, Any]]:
    """Executa N nós em paralelo e agrega payloads por id (JoinNode).

    - MAX_CHILDREN é aplicado aqui (largura máxima).
    - Cada filho é executado como sub-etapa; falha vira payload {'error': ...}
      para o join decidir — nunca morte silenciosa.
    """
    if len(children) > runner.limits.max_children:
        raise RuntimeError(f"MAX_CHILDREN excedido ({len(children)} > {runner.limits.max_children})")
    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max(1, len(children))) as pool:
        futures = {pool.submit(runner._execute_node, n, state, 0): n for n in children}
        for fut, node in futures.items():
            output = fut.result()
            runner.bus.emit(Event("transition", parent_id, f"fan-out: {node.id} {'ok' if output.ok else 'FALHOU'}", {"child": node.id}))
            results[node.id] = output.payload if output.ok else {"error": output.error}
    return results