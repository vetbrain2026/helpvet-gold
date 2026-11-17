# Extrator determinístico — projeto (r1b-0.1)

Converte o PDF de prontuário da Help Vet no JSON ouro do contrato 1.2, **sem LLM** (PROC-005). O que a regra não reconhece com certeza **não é inventado**: vai para a **quarentena**.

## Princípio: três confianças
1. **Núcleo estrutural (alta confiança)** — extraído por regra/âncora, entra no ouro direto:
   tabela do topo (paciente), pesos, temperatura, FC, FR, glicemia, PAS, ECC, datas,
   formulários `(x) Em dia`, blocos de receita (medicamento + dose + frequência + via),
   títulos de exame, carimbos de autoria, identidade do bloco (chave).
2. **Dicionário (média confiança)** — termos clínicos e abreviações de rotina reconhecidos
   por um **léxico** controlado (ver `fixtures/sinteticos/lexico_*.json`): mucosas, linfonodos,
   sintomas e sinais conhecidos, negações ("nega", "ausência de"). Entram com `confianca` < 1.
3. **Texto livre não reconhecido (baixa confiança)** — o que sobra do bloco depois de 1 e 2.
   **Não** é interpretado por regra frágil: o bloco vai para a **quarentena** com o motivo,
   para revisão humana e para alimentar o crescimento do léxico.

O ouro nasce **confiável e parcial**; cresce quando o léxico cresce. A taxa de quarentena
(`blocos_quarentena / blocos_total`) é a métrica que diz quanto falta.

## Ordem do pipeline (cada etapa opera sobre a saída da anterior)
1. **PDF → texto** (determinístico; biblioteca local, sem nuvem).
2. **Scrub de PII** (§ PII) — determinístico e idempotente: `scrub(scrub(x)) == scrub(x)`.
3. **Segmentação em blocos** + **identidade** (chave: tipo_bruto, carimbo, ordinal).
4. **Parsers estruturais** (núcleo de alta confiança).
5. **Anotador por léxico** (média confiança) — inclui a **varredura obrigatória** de mucosas e linfonodos.
6. **Quarentena** do que restou não reconhecido.
7. **Validação** contra o esquema 1.2 + regras semânticas; falha → quarentena, nada gravado.

## Varredura obrigatória (mucosas, linfonodos, TPC)
Em todo bloco de exame físico, o anotador **tem de procurar** mucosas, linfonodos e TPC.
- Encontrou e reconheceu no léxico → achado/medida com `confianca` alta.
- Encontrou o rótulo mas não a descrição (ex.: "mucosas" seguido de abreviação fora do léxico)
  → **quarentena** do bloco (`tipo_falha = termo_fora_do_lexico`), não um achado adivinhado.
- Não encontrou o rótulo → nada (ausência de menção não é achado).

## Abreviações: dicionário, não adivinhação
O léxico de abreviações (`fixtures/sinteticos/lexico_abreviacoes.json`) mapeia abreviação → termo.
**Semente** (expandir com a lista do Rafa; cada entrada é conhecimento clínico dele):
`nc`→normocoradas, `hipoc`→hipocoradas, `ict`→ictéricas, `abd`→abdome, `tpc`→tempo de preenchimento capilar,
`fc`→frequência cardíaca, `fr`→frequência respiratória, `ecc`→escore de condição corporal,
`pas`→pressão arterial sistólica, `mv`→murmúrio vesicular, `bpm`→batimentos por minuto,
`lnn`→linfonodos, `sv`→sem alterações (confirmar com o Rafa — ambíguo).
Abreviação **fora** do léxico num ponto clínico → quarentena, nunca um palpite.

## O que o extrator NUNCA faz (espelho das regras da v2.1)
- Não infere diagnóstico não escrito; não completa dose, via ou duração ausentes.
- Não traduz nem corrige nomes de fármaco ("Ibsulina" permanece).
- Não emite nome de pessoa; se a varredura de PII achar um, o paciente vai para a quarentena (`pii_detectada`), nada é gravado.
- Não usa conhecimento externo para "confirmar" o que o prontuário não diz.

## PII (determinístico, idempotente) — camadas em ordem fixa
1. Linha de autoria `Por <NOME> em <data>` → `Por [PROFISSIONAL] em <data>`.
2. Canários do cabeçalho do PDF (tutor, nome do animal, profissionais) → `[TUTOR]`, `[ANIMAL]`, `[PROFISSIONAL]` (sem acento/caixa; palavra inteira; < 3 letras ignoradas).
3. Regex estruturais: CPF (com e sem pontuação), telefone BR, e-mail, CEP, CRMV.
4. Prefixo clínico (`Dr.`, `Dra.`, `MV`…) + nome → `[PROFISSIONAL]`.
5. Palavra de relação (`tutor(a)`, `responsável`, `mãe`…) + nome → relação **mantida** + `[PESSOA_RELACIONADA]`.
6. Nome **isolado** sem âncora: **não** é substituído por regex (destruiria texto clínico). Vai para revisão amostral.
**Varredura pós-extração** sobre todo o JSON: qualquer PII estrutural ou canário (exceto ambíguo em minúscula) = **falha dura**, paciente para a quarentena.
Ambíguos (nome que é palavra clínica: "Rosa", "Mel", "Branca"): em minúscula **não** substitui (conta como revisão); em Maiúscula substitui (privacidade primeiro).

## Quarentena (estado operacional, nunca dado clínico)
Registra: `paciente_id`, `bloco_id`, `tipo_falha`, `motivo_detalhe` (tipo, posição, contagem — **nunca o valor**), `tentativas`, caminho do arquivo de debug (**fora do repo**), `criado_em`.
`tipo_falha`: `pii_detectada`, `termo_fora_do_lexico`, `substring_invalida`, `json_invalido`, `enum_invalido`, `ref_inexistente`, `chave_invalida`.
Falha de PII é dura: nada do paciente entra no ouro.

## O que é determinístico vs. o que vai para a quarentena (resumo honesto)
| Dado | Como sai |
|---|---|
| Paciente (topo), pesos, temperatura, FC/FR, glicemia, PAS, ECC, TPC | parser estrutural — alta confiança |
| Datas, formulários (x), títulos de exame, blocos de receita | parser estrutural — alta confiança |
| Mucosas, linfonodos (rótulo + descrição no léxico) | anotador por léxico — média confiança |
| Sintomas/sinais no léxico, com negação explícita | anotador por léxico — média confiança |
| Diagnóstico com hedge nuançado, sintoma fora do léxico, texto livre longo | **quarentena** |
| Nome de pessoa isolado detectado na saída | **quarentena (pii_detectada)** |
