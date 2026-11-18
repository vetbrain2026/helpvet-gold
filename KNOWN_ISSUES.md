# KNOWN_ISSUES

## KNOWN-004 — Fronteira de nome do prefixo clínico é heurística

A defesa do rótulo no prefixo clínico é **estrutural**: um **único token** colado a pontuação (`:` ou `,`) logo após o título é tratado como rótulo (ex.: "Responsável:", "Assinado:", "Visto:"), não como nome, e o trecho fica inalterado — vale para **qualquer rótulo** de uma palavra, independente de lista. Se há **mais de um token** antes da pontuação, o 1º é nome real → **redige** (cortando o verbo pela lista) e **preserva a pontuação** no fim (ex.: `Dr. Marcos Solicitou: ...` → `Dr. [PROFISSIONAL] Solicitou: ...`). A lista de parada (`_STOP_PREFIXO`) é só **reforço** para o caso **sem pontuação**: corta o nome no 1º **verbo ou achado clínico capitalizado** (ex.: "Avaliou", "Tórax"); é finita e incompleta por natureza.

Resíduos deferidos à camada de nomes na narrativa e à 2ª leitura do revisor técnico antes do portão do extrator:

- (a) nome de **um único token** imediatamente antes de `:`/`,` (ex.: `Dr. Marcos: ...`) — indistinguível de um rótulo de uma palavra, fica para a narrativa; **rótulo de duas palavras** (`Médico Responsável:`) é o resíduo espelhado e raro no outro sentido (redige por engano);
- (b) nome com **mais tokens que o teto** (4+), além dos 3 capturados após o título;
- (c) **verbo ou achado clínico capitalizado fora da lista** de parada, no caso sem pontuação.

## KNOWN-005 — Fronteira de nome da palavra de relação é heurística

Mesma fronteira heurística do prefixo clínico (KNOWN-004), agora na camada de palavra de relação (`tutora`, `responsável`, `mãe` + nome → `[PESSOA_RELACIONADA]`). A defesa do rótulo é **estrutural** por pontuação: só um **único token** colado a `:`/`,` depois da relação é rótulo (ex.: `Visto:`), válida para **qualquer rótulo** de uma palavra, independente de lista. Com **mais de um token** antes da pontuação, o 1º é nome real → **redige** e **preserva a pontuação** no fim (ex.: `responsável Maria Assinou: ...` → `responsável [PESSOA_RELACIONADA] Assinou: ...`). A lista de parada (`_STOP_RELACAO`) é só **reforço incompleto** para o caso sem pontuação: corta o nome no 1º verbo/particípio capitalizado (ex.: "Orientada").

Resíduos deferidos à camada de nomes na narrativa e à 2ª leitura oficial do PC antes do portão:

- (a) nome de **um único token** imediatamente antes de `:`/`,` — indistinguível de rótulo de uma palavra, fica para a narrativa; **rótulo de duas palavras** (`Médico Responsável:`) é o resíduo espelhado e raro;
- (b) nome com **4+ tokens**, além dos 3 capturados após a relação;
- (c) **particípio ou verbo capitalizado fora da lista** de parada, no caso sem pontuação;
- (d) formato de campo `Tutora: <nome>` (dois-pontos colado à **própria palavra de relação**) **não** é tratado aqui — fica para a camada de **canários do cabeçalho**.

## KNOWN-003 — Quarentena alta no texto livre nuançado (por desenho)

A extração determinística tem quarentena alta no texto livre nuançado por desenho (PROC-005); o léxico cresce com a revisão da quarentena; reavaliar LLM local só com outra máquina.

## KNOWN-002 — Verificador de PII barra sequências numéricas longas soltas

O verificador de PII barra qualquer sequência solta de 10, 11 ou 14 dígitos (telefone/CPF/CNPJ sem pontuação). É proposital (falhar seguro): ao escrever fixtures sintéticas, evite números longos sem pontuação, inclusive carimbos de tempo Unix em segundos. Falso positivo se resolve reescrevendo o número, nunca afrouxando o verificador.

## KNOWN-001 — Sem proteção de branch no GitHub

O GitHub não aplica proteção de branch neste plano; controle compensatório = hook `no-commit-to-branch` + o agente nunca faz merge. (Mesmo caso do KNOWN-036 do vetbrain-platform.)
