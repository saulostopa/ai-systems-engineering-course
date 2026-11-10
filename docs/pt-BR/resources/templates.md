# Templates

Templates **prontos para copiar** — o pacote de harness básico, versionado na
raiz deste repositório em `templates/`.

## Instalação somente dos templates

```sh
cp -r templates/ <seu-projeto>/
cd <seu-projeto>
./init.sh          # valida o ambiente e imprime os próximos passos
```

Essa cópia leva apenas o esqueleto instrucional. Para o núcleo executável com
scripts, hooks e diretórios de planos de execução, use o instalador standalone:

```bash
./harness-basic/install.sh /caminho/absoluto/do/projeto
```

Uma distribuição derivada no padrão do curso também pode instalar sete skills
em `.agents/skills/` e expor `./install.sh --self` quando pacote e destino são,
intencionalmente, a mesma pasta. Essas capacidades não fazem parte de uma
cópia bruta de `templates/`.

## Conteúdo do pacote

| Arquivo | Papel | Aula relacionada |
|---|---|---|
| [`AGENTS.md`](https://github.com/saulostopa/ai-systems-engineering-course/tree/main/templates/AGENTS.md) | Roteador: o que ler, como escolher, como verificar, como terminar | 04 |
| `feature_list.json` | Fonte de verdade do escopo (estado por feature) | 08 |
| `progress.md` | Diário da sessão atual | 05 |
| `session-handoff.md` | Bilhete para a próxima sessão (cabeçalho obrigatório) | 05 |
| `exec-plan.md` | Rota de uma feature para `docs/exec-plans/` (camada grande) | 13 |
| `policies/scope-control.md` | Escopo declarado antes de editar | 07 |
| `policies/definition-of-done.md` | Critérios verificáveis de "pronto" | 09 |
| `policies/evidence-required.md` | Formato de evidência (comando → esperado → real) | 09 |
| `init.sh` | Inicialização do ambiente | 06 |
| `README.md` | Instruções de instalação e personalização | — |

Cada arquivo vem com comentários de onde personalizar e a referência à aula
que o fundamenta.

## Como usar no curso

1. **Projeto 02** constrói um pacote como este do zero — compare o seu com o oficial.
2. **Projeto 04** adiciona o domínio (skills próprias) em cima deste esqueleto.
3. **Projeto 05** adiciona o contexto da área em cima dele.

::: tip Status
Este esqueleto de templates é a Story **A4**. O núcleo executável com gates
mecânicos é a Story **B1** (EPIC B); o perfil padrão de skills é a distribuição
usada pelo harness completo do curso.
:::
