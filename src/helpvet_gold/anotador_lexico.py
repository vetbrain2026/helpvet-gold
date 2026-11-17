"""Anotador por lexico (media confianca), com a varredura obrigatoria de mucosas/linfonodos/TPC.

Esqueleto r1b-0.1. Unica regra ativa: `classificar_termo`, a invariante de desenho
"termo fora do lexico vai para a quarentena, nunca vira achado adivinhado".
"""

from __future__ import annotations

from dataclasses import dataclass, field

from helpvet_gold.quarentena import TipoFalha
from helpvet_gold.segmentacao import Bloco

Registro = dict[str, object]


@dataclass(frozen=True)
class Lexico:
    """Lexico controlado. `abreviacoes`: abreviacao -> termo. `achados`: sistema -> termos."""

    abreviacoes: dict[str, str]
    achados: dict[str, list[str]]


@dataclass
class Anotacao:
    """Resultado da anotacao de um bloco. `falha` preenchida = bloco vai para a quarentena."""

    achados: list[Registro] = field(default_factory=list)
    medidas: list[Registro] = field(default_factory=list)
    falha: TipoFalha | None = None


def classificar_termo(termo: str, lexico: Lexico) -> TipoFalha | None:
    """None se o termo (ou a abreviacao) esta no lexico; senao `termo_fora_do_lexico`."""
    chave = termo.strip().lower()
    if chave in lexico.abreviacoes:
        return None
    if any(chave in termos for termos in lexico.achados.values()):
        return None
    return "termo_fora_do_lexico"


def anotar(bloco: Bloco, lexico: Lexico) -> Anotacao:
    """Anota o bloco pelo lexico. Pendente."""
    raise NotImplementedError("anotador_lexico.anotar: implementacao em PR incremental")


def varredura_obrigatoria(bloco: Bloco, lexico: Lexico) -> Anotacao:
    """Em bloco de exame fisico, procura mucosas, linfonodos e TPC.

    Rotulo + descricao no lexico -> achado/medida; rotulo sem descricao reconhecida ->
    `falha = termo_fora_do_lexico`; sem rotulo -> nada. Pendente.
    """
    raise NotImplementedError("anotador_lexico.varredura_obrigatoria: PR incremental")
