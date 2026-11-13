# CLAUDE.md — helpvet-gold

Extrator determinístico e local, sem LLM, dos prontuários da Help Vet (frente 2, extração). A extração recomeça do zero (PROC-004). Decisões: `docs/DECISOES.md`.

## Regras da frente 2 (valem para sempre)

- Uma chamada por mensagem, em primeiro plano, sem background, sem Monitor, sem subagentes. Uma edição por chamada. Todo comando com `cd … || exit`.
- NÃO faça merge. O agente nunca faz merge. Pare na PAUSA antes do push.
- Você só lê e escreve dentro da pasta do repositório helpvet-gold, com uma única exceção nomeada: ler o arquivo do prompt que o Rafa indicar e gravar relatórios em `C:\Users\rafa_\dev\relatorios-helpvet-gold\` (fora do repo, fora da Área de Trabalho e do OneDrive). Nada mais fora do repo.
- Nunca abra, liste o conteúdo, copie nem leia:
  - `C:\Users\rafa_\Arquivo_Legado\` (onde ficam o vet-extractor e o clone do vetbrain-extractor) e os caminhos antigos deles (`C:\Users\rafa_\vet-extractor`, `C:\Users\rafa_\dev\vetbrain-extractor`), caso a mudança ainda não tenha sido feita;
  - `C:\Users\rafa_\DadosClinicos\` e o caminho antigo do acervo (`C:\Users\rafa_\Desktop\Desktop\dados_clinicos_helpvet`);
  - qualquer PDF, JSON, CSV, TXT ou imagem fora do repo;
  - discos externos;
  - pastas de outros projetos.
- O código antigo de extração não é lido nem reutilizado (PROC-004).
- Nenhum dado real no repositório, nunca. Só dado sintético, inventado. Na dúvida, não entra.
- Nenhum LLM, API externa ou serviço de nuvem no código do extrator.
- Nunca copiar segredo para relatório, documentação ou commit.

## Fluxo

- Cadeia: Agente → Claude (chat do Project) → Rafa.
- PAUSA antes do push: o agente grava o relatório, resume na conversa e espera a revisão do Claude. Depois da revisão: push, PR, e pare com o link. O merge é do Rafa.
- Staging por lista explícita: `git add arquivo1 arquivo2`, nunca `git add .` nem `git add -A`.
- Bronze e prata nunca saem da máquina.
- O ouro desidentificado nunca entra em repositório nem CI (só contrato e métricas agregadas).

## Proteções

- Todo clone novo roda `uv run pre-commit install` antes do primeiro commit.
- Hooks: `no-commit-to-branch` (main), `detect-private-key`, `check-added-large-files` (500 KB), `scripts/check_pii_patterns.py` e `scripts/check_allowed_paths.py`.
- `.gitignore` bloqueia dado por padrão; exceção só para `.md`, `.txt` e `.json` em `fixtures/sinteticos/` e `contrato/`.
- Strings fictícias de PII nos testes são montadas por concatenação em tempo de execução.
