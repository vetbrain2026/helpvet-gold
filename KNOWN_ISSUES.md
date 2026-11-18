# KNOWN_ISSUES

## KNOWN-004 — Fronteira de nome do prefixo clínico é heurística

A defesa do rótulo no prefixo clínico é **estrutural**: um token colado a pontuação (`:` ou `,`) logo após o título é tratado como rótulo (ex.: "Responsável:", "Assinado:", "Visto:"), não como nome, e o trecho fica inalterado — vale para **qualquer rótulo**, independente de lista. A lista de parada (`_STOP_PREFIXO`) é só **reforço** para o caso **sem pontuação**: corta o nome no 1º **verbo ou achado clínico capitalizado** (ex.: "Avaliou", "Tórax"); é finita e incompleta por natureza.

Resíduos deferidos à camada de nomes na narrativa e à 2ª leitura do revisor técnico antes do portão do extrator:

- (a) nome **adjacente** à pontuação, quando a pontuação vem depois do próprio nome e não de um rótulo (ex.: `Dr. Marcos Silva: ...`) — a pontuação para no nome e o preserva;
- (b) nome com **mais tokens que o teto** (4+), além dos 3 capturados após o título;
- (c) **verbo ou achado clínico capitalizado fora da lista** de parada, no caso sem pontuação.

## KNOWN-003 — Quarentena alta no texto livre nuançado (por desenho)

A extração determinística tem quarentena alta no texto livre nuançado por desenho (PROC-005); o léxico cresce com a revisão da quarentena; reavaliar LLM local só com outra máquina.

## KNOWN-002 — Verificador de PII barra sequências numéricas longas soltas

O verificador de PII barra qualquer sequência solta de 10, 11 ou 14 dígitos (telefone/CPF/CNPJ sem pontuação). É proposital (falhar seguro): ao escrever fixtures sintéticas, evite números longos sem pontuação, inclusive carimbos de tempo Unix em segundos. Falso positivo se resolve reescrevendo o número, nunca afrouxando o verificador.

## KNOWN-001 — Sem proteção de branch no GitHub

O GitHub não aplica proteção de branch neste plano; controle compensatório = hook `no-commit-to-branch` + o agente nunca faz merge. (Mesmo caso do KNOWN-036 do vetbrain-platform.)
