"""Scrub e varredura de PII (deterministicos).

ESQUELETO r1b-0.5: ativas as camadas estruturais CPF, e-mail, CNPJ, telefone, CEP, CRMV,
autoria (linha ``Por <nome> em <data>``) e prefixo clinico (``Dr.``, ``Dra.``,
``Med. Vet.``).
Pendentes: canarios, palavra de relacao e nomes na narrativa
(precondicao do portao): ver docs/EXTRATOR_DETERMINISTICO.md.

O CEP so casa o formato com hifen (5 digitos, hifen, 3), nunca 8 digitos corridos. O CRMV e
ancorado na palavra CRMV, caso-insensivel (privacidade primeiro), com UF e numero opcionais.
A autoria so casa quando ha os tres sinais juntos: ``Por`` com P maiusculo, nome(s)
capitalizado(s) logo depois e a ancora ``em <data>`` (dd/mm/aaaa) em seguida.
O prefixo clinico mantem o titulo (Dr., Dra., Med. Vet.) e redige so o nome. ``MV`` NAO e
ancora: colide com murmúrio vesicular.

Principio: o scrub roda sobre texto clinico, entao exagerar destrói dado. As camadas pegam
so PII com sinal estrutural claro; o telefone nunca casa quatro digitos, hifen e quatro
digitos soltos, sem DDD (colide com faixas de referencia clinicas).
"""

from __future__ import annotations

import re

_AUTORIA = re.compile(
    r"(\bPor\s+)([A-ZÀ-ÖØ-Þ][\w.]*(?:\s+[A-ZÀ-ÖØ-Þ][\w.]*)*)(\s+em\s+\d{1,2}/\d{1,2}/\d{2,4})"
)

_PREFIXO = re.compile(
    r"((?:Dra?\.?|M[ée]d\.?\s*Vet\.?|M[ée]dico\s+Veterin[áa]rio)\s+)"
    r"([A-ZÀ-ÖØ-Þ][\w.]*(?:\s+[A-ZÀ-ÖØ-Þ][\w.]*){0,2})"
)

# Finita e incompleta — expandir conforme a 2a leitura do revisor (KNOWN-004).
_STOP_PREFIXO: frozenset[str] = frozenset(
    {
        "avaliou",
        "solicitou",
        "prescreveu",
        "realizou",
        "observou",
        "examinou",
        "atendeu",
        "relatou",
        "encaminhou",
        "evoluiu",
        "apresentou",
        "orientou",
        "recomendou",
        "indicou",
        "administrou",
        "aplicou",
        "internou",
        "suturou",
        "drenou",
        "puncionou",
        "auscultou",
        "palpou",
        "medicou",
        "retornou",
        "compareceu",
        "responsável",
        "responsavel",
        "solicitante",
        "executante",
        "tórax",
        "torax",
        "abdome",
        "abdômen",
        "abdomen",
        "mucosas",
        "paciente",
    }
)

_CRMV = re.compile(r"CRMV[\s/-]?[A-Z]{0,2}[\s:.\-]*(?:n[ºo.]?\s?)?[0-9]{2,7}", re.IGNORECASE)
_CEP = re.compile(r"(?<![0-9])[0-9]{5}-[0-9]{3}(?![0-9])")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
_CNPJ = re.compile(r"(?<![0-9])[0-9]{2}\.?[0-9]{3}\.?[0-9]{3}/?[0-9]{4}-?[0-9]{2}(?![0-9])")
_CPF = re.compile(r"(?<![0-9])[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}-?[0-9]{2}(?![0-9])")
_TELEFONES = (
    re.compile(r"(?<![0-9])(?:\+55\s?)?\(?[1-9][0-9]\)?[\s.-]?9?[0-9]{4}[\s.-]?[0-9]{4}(?![0-9])"),
    re.compile(r"(?<![0-9])9[0-9]{4}-[0-9]{4}(?![0-9])"),
    re.compile(r"(?<![0-9])[0-9]{10}(?![0-9])"),
)

# (classe, marcador, padroes) na ordem de aplicacao: CRMV, e-mail, CNPJ, CPF, CEP, telefone.
_CAMADAS: tuple[tuple[str, str, tuple[re.Pattern[str], ...]], ...] = (
    ("crmv", "[CRMV]", (_CRMV,)),
    ("email", "[EMAIL]", (_EMAIL,)),
    ("cnpj", "[CNPJ]", (_CNPJ,)),
    ("cpf", "[CPF]", (_CPF,)),
    ("cep", "[CEP]", (_CEP,)),
    ("telefone", "[TELEFONE]", _TELEFONES),
)


def _scrub_autoria(texto: str) -> str:
    return _AUTORIA.sub(r"\1[PROFISSIONAL]\3", texto)


def _varrer_autoria(texto: str) -> list[tuple[str, int]]:
    return [("autoria", m.start()) for m in _AUTORIA.finditer(texto)]


def _cortar_nome_prefixo(tokens: list[str]) -> list[str]:
    for i, tok in enumerate(tokens):
        if tok.lower().strip(".") in _STOP_PREFIXO:
            return tokens[:i]
    return tokens


def _scrub_prefixo(texto: str) -> str:
    def _sub(m: re.Match[str]) -> str:
        titulo = m.group(1)
        tokens = m.group(2).split()
        nome = _cortar_nome_prefixo(tokens)
        if not nome:
            return m.group(0)
        resto = tokens[len(nome) :]
        saida = titulo + "[PROFISSIONAL]"
        if resto:
            saida += " " + " ".join(resto)
        return saida

    return _PREFIXO.sub(_sub, texto)


def _varrer_prefixo(texto: str) -> list[tuple[str, int]]:
    achados: list[tuple[str, int]] = []
    for m in _PREFIXO.finditer(texto):
        tokens = m.group(2).split()
        nome = _cortar_nome_prefixo(tokens)
        if nome:
            achados.append(("prefixo", m.start()))
    return achados


def scrub(texto: str, canarios: frozenset[str]) -> str:
    """Remove PII do texto. Idempotente: scrub(scrub(x)) == scrub(x).

    Parcial: camadas estruturais, autoria e prefixo clinico.
    `canarios` ainda nao e usado (camada 2 pendente).
    """
    texto = _scrub_autoria(texto)
    texto = _scrub_prefixo(texto)
    for _classe, marcador, padroes in _CAMADAS:
        for padrao in padroes:
            texto = padrao.sub(marcador, texto)
    return texto


def _varrer_texto(texto: str) -> list[tuple[str, int]]:
    achados: list[tuple[str, int]] = []
    for m in _AUTORIA.finditer(texto):
        achados.append(("autoria", m.start()))
    texto = _AUTORIA.sub(lambda m: "#" * len(m.group()), texto)
    for m in _PREFIXO.finditer(texto):
        tokens = m.group(2).split()
        nome = _cortar_nome_prefixo(tokens)
        if nome:
            achados.append(("prefixo", m.start()))
    texto = _PREFIXO.sub(lambda m: "#" * len(m.group()), texto)
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
    Classes: "autoria", "prefixo", "crmv", "email", "cnpj", "cpf", "cep", "telefone".
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
