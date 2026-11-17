# Changelog

## Contrato `helpvet-gold-1.2` (2026-11-17)

Mudanças 1.1 → 1.2:

- **TPC** (tempo de preenchimento capilar) entra como medida (`medida.tipo = tpc`).
- **Mucosas** e **linfonodos** entram como achados de exame físico, com `achado_tipo` controlado (`mucosas`, `linfonodos`, `hidratacao`, `tpc`, `generico`); varredura obrigatória do bloco de exame físico.
- **`medicacao_administrada`** entra como categoria de procedimento, separada da prescrição. **Sondagem** é `procedimento_ambulatorial` com descrição literal.
- Extração determinística (PROC-005): `extracao.modelo_1b` e `extracao.versao_prompt_1b` viram `extracao.versao_regras_1b`; `inventario.blocos_llm` e `inventario.tokens_*` viram `inventario.blocos_anotados` e `inventario.blocos_quarentena`.
- Esquema executável `contrato/helpvet-gold-1.2.schema.json` (JSON Schema 2020-12), exemplo sintético `fixtures/sinteticos/exemplo_ouro.json` e teste `tests/test_contrato.py`.
