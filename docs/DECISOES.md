# Decisões que governam o repositório

Referência completa: Project do VetBrain (chat do Claude). Aqui, só o resumo.

## PROC-001 — Extrator determinístico e local, sem LLM
O extrator da Help Vet é determinístico e roda localmente. Nenhum LLM, API externa ou serviço de nuvem no código do extrator.

## PROC-003 — Dado real nunca sai da máquina
Bronze e prata nunca saem da máquina. O ouro desidentificado nunca entra em repositório nem em CI; só contrato e métricas agregadas. Nenhum dado real no repositório: só dado sintético, inventado.

## PROC-004 — Extração recomeça do zero
O código antigo de extração não é lido nem reutilizado. Este repositório começa limpo, com a fundação (proteções, estrutura, CI e regras) antes de qualquer linha de extração.
