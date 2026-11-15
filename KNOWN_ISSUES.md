# KNOWN_ISSUES

## KNOWN-002 — Verificador de PII barra sequências numéricas longas soltas

O verificador de PII barra qualquer sequência solta de 10, 11 ou 14 dígitos (telefone/CPF/CNPJ sem pontuação). É proposital (falhar seguro): ao escrever fixtures sintéticas, evite números longos sem pontuação, inclusive carimbos de tempo Unix em segundos. Falso positivo se resolve reescrevendo o número, nunca afrouxando o verificador.

## KNOWN-001 — Sem proteção de branch no GitHub

O GitHub não aplica proteção de branch neste plano; controle compensatório = hook `no-commit-to-branch` + o agente nunca faz merge. (Mesmo caso do KNOWN-036 do vetbrain-platform.)
