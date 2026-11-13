# helpvet-gold

Extrator determinístico e local (sem LLM) dos prontuários da Help Vet. A extração recomeça do zero (PROC-004). Decisões que governam o repo: [docs/DECISOES.md](docs/DECISOES.md).

## ⚠️ Todo clone novo: rode isto antes do primeiro commit

```bash
uv run pre-commit install
```

Sem isso, os hooks não bloqueiam nada.

## O que NÃO entra neste repositório

- Dado real: nenhum nome, data, telefone, CPF, PDF ou trecho de prontuário real. Só dado sintético, inventado (`fixtures/sinteticos/`).
- LLM, API externa ou serviço de nuvem no código do extrator.

## Como rodar os testes

```bash
uv sync
uv run pytest
uv run ruff check
uv run ruff format --check
uv run mypy src
uv run pre-commit run --all-files
```
