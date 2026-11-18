# KNOWN_ISSUES

## KNOWN-004 — Fronteira de nome do prefixo clínico é heurística

A fronteira de nome do prefixo clínico é heurística: a lista de parada é finita e incompleta; nome após rótulo (ex.: "Responsável: &lt;nome&gt;") e substantivo clínico capitalizado logo após o título, fora da lista, podem não ser tratados. Resíduo deferido à camada de nomes na narrativa e à 2ª leitura do revisor técnico antes do portão do extrator.

## KNOWN-003 — Quarentena alta no texto livre nuançado (por desenho)

A extração determinística tem quarentena alta no texto livre nuançado por desenho (PROC-005); o léxico cresce com a revisão da quarentena; reavaliar LLM local só com outra máquina.

## KNOWN-002 — Verificador de PII barra sequências numéricas longas soltas

O verificador de PII barra qualquer sequência solta de 10, 11 ou 14 dígitos (telefone/CPF/CNPJ sem pontuação). É proposital (falhar seguro): ao escrever fixtures sintéticas, evite números longos sem pontuação, inclusive carimbos de tempo Unix em segundos. Falso positivo se resolve reescrevendo o número, nunca afrouxando o verificador.

## KNOWN-001 — Sem proteção de branch no GitHub

O GitHub não aplica proteção de branch neste plano; controle compensatório = hook `no-commit-to-branch` + o agente nunca faz merge. (Mesmo caso do KNOWN-036 do vetbrain-platform.)
