# CONTRATO JSON OURO — `helpvet-gold-1.2`

Um arquivo **por paciente**, congelado e versionado depois de validado. Esquema executável: `contrato/helpvet-gold-1.2.schema.json`. Mudança de contrato = nova versão + migração.

Extração **determinística** (sem LLM, PROC-004): a Fase 1a segmenta e identifica os blocos; a anotação clínica (Fase 1b) é por **regras + dicionário**, com **quarentena** para o que a regra não reconhece com certeza. O que não é reconhecido não é inventado: vai para a fila de revisão.

## Mudanças 1.1 → 1.2
- **TPC** (tempo de preenchimento capilar) entra como medida.
- **Mucosas** e **linfonodos** entram como achados de exame físico, com descrição controlada, e o extrator é **obrigado a varrer** o bloco de exame físico atrás deles.
- **`medicacao_administrada`** entra como categoria de procedimento (ato de aplicar medicação no atendimento, ex.: "atropina IV"), separada da prescrição (receita). **Sondagem** é procedimento (`procedimento_ambulatorial`, descrição literal).
- Como a extração é determinística, o bloco `extracao` troca `modelo_1b`/`versao_prompt_1b` por **`versao_regras_1b`**; o `inventario` troca `blocos_llm`/`tokens_*` por **`blocos_anotados`** e **`blocos_quarentena`**.

## 1. Estrutura

```jsonc
{
  "contrato": "helpvet-gold-1.2",
  "extracao": {
    "run_id": 101,
    "iniciado_em": "2026-11-02T10:00:00",
    "pdf_sha256": "…64 hex…",            // hash do PDF original (o arquivo fica local, nunca no repo)
    "paginas_total": 44,
    "versao_extrator_1a": "0.1.0",       // inclui versão do scrub de PII e do strip de template
    "versao_regras_1b": "r1b-0.1",       // versão do conjunto de regras + dicionário de anotação
    "status": "ok | parcial | falha"
  },
  "paciente": {
    "codigo_sistema": "838",             // numérico; no banco vira 'helpvet:838'
    "especie": "canina | felina | outra",
    "raca": "SRD | Lhasa Apso | …",
    "sexo": "M | F | desconhecido",
    "castrado": 0,                       // 0/1/null
    "data_nascimento": "2014-05-04",     // ISO ou null
    "nascimento_confianca": 0.9,
    "grupo_tutor_ref": null              // SEMPRE null; o validador recusa outro valor
  },
  "eventos": [ /* §2 */ ],
  "alertas_extracao": [ /* §3 */ ],
  "inventario": {
    "blocos_total": 120,
    "blocos_anotados": 61,               // blocos cujo texto livre foi anotado por regra
    "blocos_quarentena": 7,              // blocos que a regra não reconheceu com certeza
    "blocos_sem_carimbo": 0,
    "blocos_descartados": {"ruido":0,"financeiro":0,"foto":0,"administrativo":0},
    "linhas_template_removidas": 0,
    "execucoes_prescricao_nao_modeladas": 74,
    "exames_imagem_paginas": [36]
  }
}
```

## 2. Evento

```jsonc
{
  "ref": "E007",                          // local ao arquivo; nunca vira chave do banco
  "chave": {                              // IDENTIDADE — vem da Fase 1a (determinística), nunca inventada
    "tipo_bruto": "Atendimento",          // rótulo literal do cabeçalho do bloco
    "subtipo": null,                      // só em "Prescrição": título normalizado
    "autoria_em": "2025-07-05T16:47",     // carimbo do bloco, ao minuto; tem de bater com o bloco
    "ordinal": 1,                         // 1..n no mesmo (tipo_bruto[/subtipo], autoria_em)
    "parte_indice": null                  // só em fragmento
  },
  "conteudo_sha1": "…40 hex…",            // sha1 do texto do bloco DESIDENTIFICADO
  "parte_de": null,                       // bloco_id original, só em fragmento
  "bloco_id": "B0042",                    // liga ao blocos.jsonl; o trecho é validado contra ESTE texto
  "tipo": "consulta_clinica",             // vocabulário §4 (normalizado; NÃO entra na identidade)
  "categoria": "clinico | administrativo | financeiro",
  "event_date": "2025-07-05",             // ISO ou null (nunca a data de impressão)
  "registered_date": "2025-07-07T18:48",
  "autor_papel": "veterinario | endocrinologista | radiologista | enfermagem | sistema | outro | null",
  "pagina_inicio": 9, "pagina_fim": 14,

  "medidas":   [ { "ref":"M1", "tipo":"peso|temperatura|fc|fr|glicemia|ecc|bhb|cetonas_fita|pas|tpc|spo2",
                   "valor": 13.2,            // número ou null (medida qualitativa: null + valor_texto)
                   "valor_texto": null,      // literal da medida qualitativa, ex.: "++"; null nas numéricas
                   "unidade": "kg | null", "data_medida": "2025-07-05T16:47",
                   "confianca": 0.95, "pagina": 14, "trecho": "Peso: 13,200 kg" } ],
  "achados":   [ { "ref":"A1", "origem":"queixa | exame_fisico", "sistema":"respiratorio|…",
                   "achado_tipo":"mucosas|linfonodos|hidratacao|tpc|generico",   // controlado; 'generico' p/ o resto
                   "descricao":"mucosas hipocoradas", "status":"presente | ausente | nao_avaliado | desconhecido",
                   "pagina": 13, "trecho":"mucosas hipocoradas", "confianca": 0.9 } ],
  "exames":    [ { "ref":"X1", "modalidade":"hemograma|ecg|… (snake_case)", "laboratorio": "DiagClin | null",
                   "status":"solicitado | resultado_textual | resultado_imagem_nao_extraido | laudo_externo | ausente",
                   "narrativa": "…", "data_laudo": "2025-07-24", "pagina": 3, "trecho": "…",
                   "analitos": [ { "codigo":"ecg_fc", "valor_texto":"96 bpm", "valor":96, "unidade":"bpm",
                                   "tipo_resultado":"estruturado | ausente", "ref_min":null, "ref_max":null,
                                   "interpretacao":"normal|alterado|reagente|nao_reagente|indefinido" } ] } ],
  "diagnosticos": [ { "ref":"D1", "termo_original":"hemoparasitose",
                      "status_evidencia":"confirmado | suspeito | descartado | achado_imagem",
                      "pagina": 29, "trecho":"Diagnóstico: hemoparasitose", "confianca": 0.6,
                      "evidencias": [ { "tipo":"achado|analito|exame", "ref":"A1", "polaridade":"a_favor|contra", "peso": null } ] } ],
  "prescricoes": [ { "ref":"R1", "medicamento_original":"Prediderm 5mg", "dose_texto":"1 cp",
                     "frequencia_horas":12, "duracao_dias":3,
                     "via":"oral|intravenosa|subcutanea|intramuscular|topica|otologica|oftalmica|inalatoria|retal|outra|null",
                     "etapa": 1, "componentes": null, "controlado": 0, "origem_produto":"vet|humano|null",
                     "pagina": 1, "trecho":"Dar 1 comprimido a cada 12h por 3 dias" } ],
  "desfechos": [ { "ref":"O1",
                   "tipo":"obito|eutanasia|alta_internacao|alta_a_pedido|transferencia|resolucao|melhora|piora",
                   "origem":"registrado | referido", "data_desfecho":"2025-03-05 | null",
                   "pagina": 3, "trecho":"Internação: Alta da internação", "confianca": 0.9 } ],
  "procedimentos": [ { "ref":"P1",
                       "categoria":"vacinacao|antiparasitario|castracao|cirurgia|sedacao_anestesia|transfusao|fluidoterapia|medicacao_administrada|procedimento_ambulatorial|outro",
                       "descricao_original":"atropina 0,04 mg/kg IV", "status":"realizado|agendado|indicado|recusado|referido",
                       "situacao":"em_dia|em_atraso|nunca|desconhecida|null",   // só vacinacao/antiparasitario
                       "data_procedimento":"2024 | 2024-05 | 2024-05-10 | null",
                       "pagina": 1, "trecho":"Atropina IV em bolus", "confianca": 0.8 } ],
  "texto_livre_resumo": null              // opcional; nunca substitui os campos estruturados
}
```

### Regras do contrato
- **Identidade**: `chave` é preenchida pela Fase 1a determinística, nunca pela anotação. O loader confere: `autoria_em` igual ao carimbo do bloco; `conteudo_sha1` igual ao hash do texto desidentificado; `subtipo` só em Prescrição; sem chave duplicada no arquivo.
- **Bloco sem carimbo** não tem chave e não entra no JSON: vai ao relatório de padrões novos da 1a.
- **Todo item clínico** (medida, achado, exame, diagnóstico, prescrição, desfecho, procedimento) tem `pagina` e `trecho` (analitos herdam do exame).
- **`trecho` é substring do BLOCO DESIDENTIFICADO** (o texto já sem PII), não do PDF. Em fragmento, do fragmento.
- **Exame sem resultado em texto**: `trecho` = título do exame (`HEMOGRAMA COMPLETO`), nunca o cabeçalho da tabela. `trecho: null` não é aceito.
- **`medida.valor` aceita número ou null.** Medida qualitativa (cetonas de fita "++", TPC "normal") tem `valor` = null e o literal em `valor_texto`; o `trecho` sempre traz a linha literal.
- **`unidade = null`** quando o texto não traz unidade (ECC, BHB, cetonas, TPC qualitativo). Se o texto traz a escala ("5/9"), a unidade é a escala literal.
- **Achado de exame físico** (`origem: exame_fisico`): `achado_tipo` usa o vocabulário controlado (`mucosas`, `linfonodos`, `hidratacao`, `tpc`) quando couber; o resto é `generico`. Mucosas e linfonodos são de **varredura obrigatória** (ver a especificação do extrator).
- **Desfecho**: só quando escrito. Ausência de retorno não é desfecho. `referido` = contado pelo tutor ou histórico.
- **Procedimento vs prescrição**: o que está em bloco de receita é `prescricao`. Procedimento é ato realizado/agendado/indicado/recusado/relatado. **Medicação aplicada no atendimento** (não em receita) é procedimento `medicacao_administrada`. **Sondagem** é `procedimento_ambulatorial` com a descrição literal. `situacao` só em vacinação e antiparasitário. Formulário `(x) Em dia` → procedimento por parser determinístico.
- `evidencias[].ref` aponta para `ref` de achado, analito ou exame do mesmo evento. `peso = null`. `polaridade` obrigatória.
- `diagnosticos[].status_evidencia`: `achado_imagem` = achado de imagem; `suspeito` = "possível", "sugestivo", "?", "a esclarecer"; `confirmado` = afirmado sem hedge ou com exame confirmatório; `descartado` = negado/excluído.
- **Não existe** `problema`, `episodio` nem `prescricao_problema` no JSON: são Fase 2.
- Desconhecido = `null` (não string vazia, não "N/A"). Nenhum campo pode conter PII; a varredura roda no arquivo inteiro, inclusive na chave.

## 3. Alertas de extração (`alertas_extracao`)

```jsonc
{ "tipo":"conflito_interno | data_inconsistente | historia_sem_registro | pareamento_incerto | dado_ausente",
  "evento_ref":"E007", "severidade":"baixa|media|alta", "descricao":"texto curto SEM PII" }
```

## 4. Vocabulário de `evento.tipo` (normalizado; ampliar só com evidência)
Fixos (15): `consulta_clinica`, `retorno_clinico`, `solicitacao_exame`, `solicitacao_hemocomponente`, `encaminhamento`, `receita`, `receituario_controle_especial`, `internacao_admissao`, `alta_internacao`, `prescricao_internacao`, `medida_isolada`, `observacao_clinica`, `termo_consentimento`, `ficha_resumida`, `comprovante`.
Famílias: `consulta_<especialidade>` e `exame_<modalidade>`.

## 5. Vocabulários controlados (espelho do esquema)
- `achado.sistema`: respiratorio, cardiovascular, digestorio, urinario, reprodutor, locomotor, neurologico, pele, ocular, ouvido, oral, endocrino, geral.
- `achado.achado_tipo`: mucosas, linfonodos, hidratacao, tpc, generico.
- `medida.tipo`: peso, temperatura, fc, fr, glicemia, ecc, bhb, cetonas_fita, pas, tpc, spo2.
- `procedimento.categoria`: vacinacao, antiparasitario, castracao, cirurgia, sedacao_anestesia, transfusao, fluidoterapia, medicacao_administrada, procedimento_ambulatorial, outro.
- `desfecho.tipo`: obito, eutanasia, alta_internacao, alta_a_pedido, transferencia, resolucao, melhora, piora.

## 6. Exemplo mínimo
`fixtures/sinteticos/exemplo_ouro.json`: eventos **inventados** (consulta com mucosas e TPC, hemograma só em imagem, peso, retorno com desfecho `melhora` e procedimento de vacinação, e uma medicação administrada). Cada bloco começa pela linha de título e pela de autoria, já desidentificadas.
