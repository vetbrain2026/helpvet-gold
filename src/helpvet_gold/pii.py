"""Scrub e varredura de PII (deterministicos).

ESQUELETO r1b-0.1: so a camada 3 parcial (CPF) esta ativa, para as invariantes de desenho
serem testaveis. As demais camadas (autoria, canarios, telefone, e-mail, CEP, CRMV, prefixo
clinico, palavra de relacao) estao pendentes: ver docs/EXTRATOR_DETERMINISTICO.md.
"""

from __future__ import annotations

import re

_CPF = re.compile(r"(?<![0-9])[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}-?[0-9]{2}(?![0-9])")
_MARCADOR_CPF = "[CPF]"


def scrub(texto: str, canarios: frozenset[str]) -> str:
    """Remove PII do texto. Idempotente: scrub(scrub(x)) == scrub(x).

    Parcial: so CPF. `canarios` ainda nao e usado (camada 2 pendente).
    """
    return _CPF.sub(_MARCADOR_CPF, texto)


def varredura(obj: object) -> list[tuple[str, int]]:
    """Varre um objeto JSON-like e devolve (classe, posicao) de cada PII achada.

    Nunca devolve o valor. A posicao e o indice dentro da string em que a PII aparece.
    Parcial: so a classe "cpf".
    """
    achados: list[tuple[str, int]] = []
    if isinstance(obj, str):
        achados.extend(("cpf", m.start()) for m in _CPF.finditer(obj))
    elif isinstance(obj, dict):
        for chave, valor in obj.items():
            achados.extend(varredura(chave))
            achados.extend(varredura(valor))
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            achados.extend(varredura(item))
    return achados
