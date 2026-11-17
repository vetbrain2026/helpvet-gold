"""Segmentacao do texto (ja sem PII) em blocos, com a identidade de cada um."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Bloco:
    """Um bloco do prontuario. `carimbo` e None em bloco sem carimbo (nao entra no ouro)."""

    id: str
    tipo_bruto: str
    carimbo: str | None
    texto: str


def segmentar(texto: str) -> list[Bloco]:
    """Divide o texto desidentificado em blocos. Pendente."""
    raise NotImplementedError("segmentacao.segmentar: implementacao em PR incremental")
