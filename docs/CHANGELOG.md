# Changelog

## scrub r1b-0.6: corrige condição de pontuação (rótulo = 1 token; nome multi-token antes de pontuação é redigido) no prefixo e na relação

A 2ª leitura do revisor achou vazamento nas duas camadas âncora: a regra `if punct: não redige` suprimia a redação sempre que havia `:`/`,` no match, mas a pontuação pode vir **depois do nome** (ex.: `responsável Maria Assinou: documento` → vazava "Maria"). `_prefixo_resultado` e `_relacao_resultado` passam a suprimir só quando o rótulo é **um único token** colado à pontuação (`if punct and len(tokens) == 1`); com nome multi-token antes da pontuação, o nome é redigido (cortando o verbo pela lista) e a pontuação é **preservada** no fim. Rótulo de uma palavra (`Visto:`, `Responsável:`) segue inalterado. Testes de não-vazamento em `tests/test_pii_prefixo.py` e `tests/test_pii_relacao.py`; KNOWN-004 e KNOWN-005 ajustados.

## scrub r1b-0.6: camada de palavra de relação (mesma defesa estrutural do prefixo)

`src/helpvet_gold/pii.py` ganha a camada de **palavra de relação**: `tutora Ana`, `responsável Carlos`, `mãe Joana` → relação **mantida** + `[PESSOA_RELACIONADA]`, redigindo só o nome. Espelha `_prefixo_resultado`: `_RELACAO` com a palavra de relação caso-insensível (flag escopado `(?i:...)`) e o nome só-maiúscula (classe explícita, sem `re.IGNORECASE` global); `_relacao_resultado` decide pela **estrutura primeiro** (token colado a `:`/`,` é rótulo → não redige, independente de lista) e usa a `_STOP_RELACAO` (verbos/particípios) só como reforço do caso sem pontuação; teto de 3 tokens. `scrub` chama `_scrub_relacao` após o prefixo; `varredura` ganha a classe `relacao`. Idempotência mantida. KNOWN-005 registrado. Testes em `tests/test_pii_relacao.py`. Canários e nomes na narrativa seguem pendentes.

## scrub r1b-0.5: prefixo com parada estrutural por pontuação (rótulo não vaza nome, independente de lista)

`src/helpvet_gold/pii.py` ganha a defesa **estrutural** do rótulo no prefixo clínico: `_PREFIXO` captura a pontuação colada (`:` ou `,`) e o helper único `_prefixo_resultado` decide pela estrutura primeiro — token colado a `:`/`,` é rótulo (ex.: `Assinado:`, `Visto:`, `Emitente:`), não nome, e o trecho fica inalterado, **para qualquer rótulo, independente de lista**. A `_STOP_PREFIXO` fica só como reforço do caso sem pontuação (verbo/achado clínico capitalizado) e os rótulos saem dela. `scrub`, `varredura` e `_varrer_texto` passam pelo mesmo helper. KNOWN-004 reescrito. Testes estruturais em `tests/test_pii_prefixo.py`.

## scrub r1b-0.5: prefixo com lista de parada e teto (corrige engolir verbo/vazar nome após rótulo)

`src/helpvet_gold/pii.py` passa a redigir prefixos clínicos (`Dr.`, `Dra.`, `Méd. Vet.`, `Médico Veterinário`) + nome → título mantido + `[PROFISSIONAL]`. `MV` **não** é âncora: colide com murmúrio vesicular (`MV Diminuído`). Nome limitado a 3 tokens capitalizados e cortado por lista de parada (verbos e rótulos clínicos); se o primeiro token é da lista, não redige (evita engolir verbo e vazar nome após rótulo). `varredura` ganha a classe `prefixo`. Limite heurístico registrado no KNOWN-004. Testes em `tests/test_pii_prefixo.py`. Palavra de relação, canários e nomes na narrativa seguem pendentes.

## scrub r1b-0.4: camada de autoria

`src/helpvet_gold/pii.py` passa a redigir a linha de autoria `Por <nome> em <data>` → `Por [PROFISSIONAL] em <data>`. Só casa com os três sinais: `Por` maiúsculo, nome(s) capitalizado(s) e âncora `em dd/mm/aaaa`. Negativos clínicos (por via oral, por 3 dias, Por favor, consulta em data, por volta de) sobrevivem. `varredura` ganha a classe `autoria`. Testes em `tests/test_pii_autoria.py`. Nomes na narrativa seguem pendentes.

## scrub r1b-0.3: camadas CEP e CRMV

`src/helpvet_gold/pii.py` passa a redigir CEP (`[CEP]`, só o formato com hífen, nunca 8 dígitos corridos) e CRMV (`[CRMV]`, ancorado na palavra CRMV, caso-insensível). Nova ordem: CRMV → e-mail → CNPJ → CPF → CEP → telefone. `varredura` ganha as classes `cep` e `crmv`. Testes em `tests/test_pii_cep_crmv.py`. Nomes na narrativa seguem pendentes.

## scrub r1b-0.2: camadas estruturais e-mail, CNPJ, telefone

`src/helpvet_gold/pii.py` passa a redigir e-mail (`[EMAIL]`), CNPJ (`[CNPJ]`) e telefone (`[TELEFONE]`, só sinais fortes), além do CPF; `varredura` ganha as classes `email`, `cnpj` e `telefone` (sem devolver o valor). Testes positivos, negativos clínicos (pesos, doses, datas e faixas não são redigidos), idempotência e varredura em `tests/test_pii_estrutural.py`. Nomes na narrativa seguem pendentes.

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
