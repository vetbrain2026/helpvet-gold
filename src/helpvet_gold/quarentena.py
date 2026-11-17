"""Quarentena: estado operacional do que a regra nao reconheceu com certeza.

Nunca guarda dado clinico nem valor de PII: so tipo, posicao e contagem.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TipoFalha = Literal[
    "pii_detectada",
    "termo_fora_do_lexico",
    "substring_invalida",
    "json_invalido",
    "enum_invalido",
    "ref_inexistente",
    "chave_invalida",
]


@dataclass(frozen=True)
class FalhaQuarentena:
    """Uma falha registrada. `motivo_detalhe` descreve tipo, posicao e contagem, nunca o valor."""

    paciente_id: str
    bloco_id: str | None
    tipo_falha: TipoFalha
    motivo_detalhe: str
    tentativas: int
    arquivo_debug: str | None  # caminho FORA do repositorio
    criado_em: str  # ISO, ao minuto


def registrar(falha: FalhaQuarentena) -> None:
    """Grava a falha na fila de quarentena (local, fora do repo). Pendente."""
    raise NotImplementedError("quarentena.registrar: implementacao em PR incremental")
