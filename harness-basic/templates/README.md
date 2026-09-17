# Pacote de harness básico — templates

Copie este pacote para a raiz de um projeto pequeno para entregar o harness
mínimo em minutos. Modelado a partir do `webmotors-harness-factory`.

## Instalação

```sh
cp -r templates/ <seu-projeto>/
cd <seu-projeto>
./init.sh          # valida o ambiente e imprime os próximos passos
chmod +x init.sh   # se o bit de execução se perdeu na cópia
```

## Conteúdo

| Arquivo | Papel | Aula |
|---|---|---|
| `AGENTS.md` | Roteador: o que ler, como escolher, como verificar, como terminar | 04 |
| `feature_list.json` | Fonte de verdade do escopo (estado por feature) | 08 |
| `claude-progress.md` | Diário da sessão atual | 05 |
| `session-handoff.md` | Bilhete para a próxima sessão (cabeçalho obrigatório) | 05 |
| `policies/scope-control.md` | Escopo declarado antes de editar | 07 |
| `policies/definition-of-done.md` | Critérios verificáveis de "pronto" | 09 |
| `policies/evidence-required.md` | Formato de evidência (comando → esperado → real) | 09 |
| `init.sh` | Inicialização do ambiente | 06 |

## Personalização mínima

1. Edite a seção 1 e 7 do `AGENTS.md` (o que é o repo, comandos reais).
2. Substitua as features de exemplo do `feature_list.json` pelas suas.
3. Se o projeto não usa Node, ajuste a seção 4 do `init.sh`.
4. (Opcional) Instale o pacote de skills: `harness-agent-skills` (veja a Biblioteca).

## Evolução natural

- Precisa de gates mecânicos? Adicione hooks de pre-commit/pre-push (Projeto 02 do curso).
- Precisa de gestão de fluxo? Use o AgEnFK em cima deste pacote.
- Precisa de contexto da área? Evolua para o Area Copilot (Projeto 05).

## Garantia

Nenhum arquivo deste pacote é "decorativo": cada um responde a uma pergunta
do agente (o quê, como, quando parar, onde estava) ou a um gate do processo
(escopo, pronto, evidência). Se um arquivo não estiver sendo lido, remova-o —
pasta de templates inchada é dívida, não rigor.