# Changelog

## Especificação do extrator `r1b-0.1`

Projeto do extrator determinístico (`docs/EXTRATOR_DETERMINISTICO.md`) e esqueleto de código com as interfaces (`pii`, `segmentacao`, `parsers_estruturais`, `anotador_lexico`, `quarentena`); léxicos semente sintéticos e testes das invariantes de desenho. `__version__` = 0.1.0. Implementação em PRs incrementais. KNOWN-003 registrado.

## Contrato `helpvet-gold-1.2` (2026-11-17)

Mudanças 1.1 → 1.2:

- **TPC** (tempo de preenchimento capilar) entra como medida (`medida.tipo = tpc`).
- **Mucosas** e **linfonodos** entram como achados de exame físico, com `achado_tipo` controlado (`mucosas`, `linfonodos`, `hidratacao`, `tpc`, `generico`); varredura obrigatória do bloco de exame físico.
- **`medicacao_administrada`** entra como categoria de procedimento, separada da prescrição. **Sondagem** é `procedimento_ambulatorial` com descrição literal.
- Extração determinística (PROC-005): `extracao.modelo_1b` e `extracao.versao_prompt_1b` viram `extracao.versao_regras_1b`; `inventario.blocos_llm` e `inventario.tokens_*` viram `inventario.blocos_anotados` e `inventario.blocos_quarentena`.
- Refinamento: `medida.valor` passa a aceitar número ou null, e `medida.valor_texto` (opcional) guarda o literal de medidas qualitativas (cetonas de fita "++", TPC "normal"). O `trecho` continua trazendo a linha literal.
- Esquema executável `contrato/helpvet-gold-1.2.schema.json` (JSON Schema 2020-12), exemplo sintético `fixtures/sinteticos/exemplo_ouro.json` e teste `tests/test_contrato.py`.
