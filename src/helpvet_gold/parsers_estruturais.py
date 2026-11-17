"""Parsers estruturais (nucleo de alta confianca). Esqueleto: so interfaces.

Retornam dicts no formato do contrato 1.2 (contrato/helpvet-gold-1.2.schema.json).
Medida numerica preenche `valor`. Medida qualitativa (cetonas de fita "++", TPC "normal")
usa `valor = None` e o literal em `valor_texto`; o `trecho` traz sempre a linha literal.
"""

from __future__ import annotations

from helpvet_gold.segmentacao import Bloco

Registro = dict[str, object]


def parse_paciente(texto: str) -> Registro:
    """Le a tabela do topo e devolve o objeto `paciente` (grupo_tutor_ref sempre None)."""
    raise NotImplementedError("parse_paciente: implementacao em PR incremental")


def parse_medidas(bloco: Bloco) -> list[Registro]:
    """Extrai peso, temperatura, FC, FR, glicemia, PAS, ECC, TPC, cetonas, BHB, SpO2."""
    raise NotImplementedError("parse_medidas: implementacao em PR incremental")


def parse_receita(bloco: Bloco) -> list[Registro]:
    """Extrai prescricoes (medicamento + dose + frequencia + via). Nao completa o que falta."""
    raise NotImplementedError("parse_receita: implementacao em PR incremental")


def parse_formulario(bloco: Bloco) -> list[Registro]:
    """Extrai formularios `(x) Em dia` como procedimentos (vacinacao, antiparasitario)."""
    raise NotImplementedError("parse_formulario: implementacao em PR incremental")


def parse_datas(bloco: Bloco) -> Registro:
    """Extrai event_date e registered_date do bloco (nunca a data de impressao)."""
    raise NotImplementedError("parse_datas: implementacao em PR incremental")
