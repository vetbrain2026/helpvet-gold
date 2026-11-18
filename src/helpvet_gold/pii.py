"""Scrub e varredura de PII (deterministicos).

ESQUELETO r1b-0.2: ativas as camadas estruturais CPF, e-mail, CNPJ e telefone. Pendentes:
autoria, canarios, prefixo clinico, palavra de relacao, CEP, CRMV e nomes na narrativa
(precondicao do portao): ver docs/EXTRATOR_DETERMINISTICO.md.

Principio: o scrub roda sobre texto clinico, entao exagerar destrói dado. As camadas pegam
so PII com sinal estrutural claro; o telefone nunca casa quatro digitos, hifen e quatro
digitos soltos, sem DDD (colide com faixas de referencia clinicas).
"""

from __future__ import annotations

import re

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
_CNPJ = re.compile(r"(?<![0-9])[0-9]{2}\.?[0-9]{3}\.?[0-9]{3}/?[0-9]{4}-?[0-9]{2}(?![0-9])")
_CPF = re.compile(r"(?<![0-9])[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}-?[0-9]{2}(?![0-9])")
_TELEFONES = (
    re.compile(r"(?<![0-9])(?:\+55\s?)?\(?[1-9][0-9]\)?[\s.-]?9?[0-9]{4}[\s.-]?[0-9]{4}(?![0-9])"),
    re.compile(r"(?<![0-9])9[0-9]{4}-[0-9]{4}(?![0-9])"),
    re.compile(r"(?<![0-9])[0-9]{10}(?![0-9])"),
)

# (classe, marcador, padroes) na ordem de aplicacao: e-mail, CNPJ, CPF, telefone.
_CAMADAS: tuple[tuple[str, str, tuple[re.Pattern[str], ...]], ...] = (
    ("email", "[EMAIL]", (_EMAIL,)),
    ("cnpj", "[CNPJ]", (_CNPJ,)),
    ("cpf", "[CPF]", (_CPF,)),
    ("telefone", "[TELEFONE]", _TELEFONES),
)


def scrub(texto: str, canarios: frozenset[str]) -> str:
    """Remove PII do texto. Idempotente: scrub(scrub(x)) == scrub(x).

    Parcial: so as camadas estruturais. `canarios` ainda nao e usado (camada 2 pendente).
    """
    for _classe, marcador, padroes in _CAMADAS:
        for padrao in padroes:
            texto = padrao.sub(marcador, texto)
    return texto


def _varrer_texto(texto: str) -> list[tuple[str, int]]:
    achados: list[tuple[str, int]] = []
    for classe, _marcador, padroes in _CAMADAS:
        for padrao in padroes:
            # Casamentos ja consumidos viram "#" (mesmo tamanho): as posicoes se mantem e a
            # mesma PII nao e contada em duas classes, como no scrub.
            for m in list(padrao.finditer(texto)):
                achados.append((classe, m.start()))
            texto = padrao.sub(lambda m: "#" * len(m.group()), texto)
    return sorted(achados, key=lambda a: a[1])


def varredura(obj: object) -> list[tuple[str, int]]:
    """Varre um objeto JSON-like e devolve (classe, posicao) de cada PII achada.

    Nunca devolve o valor. A posicao e o indice dentro da string em que a PII aparece.
    Classes: "email", "cnpj", "cpf", "telefone".
    """
    achados: list[tuple[str, int]] = []
    if isinstance(obj, str):
        achados.extend(_varrer_texto(obj))
    elif isinstance(obj, dict):
        for chave, valor in obj.items():
            achados.extend(varredura(chave))
            achados.extend(varredura(valor))
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            achados.extend(varredura(item))
    return achados
