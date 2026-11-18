"""Camadas estruturais de PII (e-mail, CNPJ, telefone). So dado sintetico, montado em runtime."""

from __future__ import annotations

import pytest

from helpvet_gold.pii import scrub, varredura

_ARROBA = "@"
EMAIL_1 = "fulano" + _ARROBA + "exemplo.com.br"
EMAIL_2 = "a.b+c" + _ARROBA + "sub.dominio.io"
CNPJ_PONTUADO = "12" + "." + "345" + "." + "678" + "/" + "0001" + "-" + "95"
CNPJ_CORRIDO = "12" + "345" + "678" + "0001" + "95"
CPF_FALSO = "111" + "." + "222" + "." + "333" + "-" + "44"
TEL_PAREN = "(11) " + "98765" + "-" + "4321"
TEL_55 = "+55 11 " + "98765" + "-" + "4321"
TEL_DDD = "11 " + "98765" + "-" + "4321"
TEL_SOLTO = "98765" + "-" + "4321"
TEL_BARE = "11" + "3456" + "7890"

POSITIVOS = [
    (EMAIL_1, "email", "[EMAIL]"),
    (EMAIL_2, "email", "[EMAIL]"),
    (CNPJ_PONTUADO, "cnpj", "[CNPJ]"),
    (CNPJ_CORRIDO, "cnpj", "[CNPJ]"),
    (TEL_PAREN, "telefone", "[TELEFONE]"),
    (TEL_55, "telefone", "[TELEFONE]"),
    (TEL_DDD, "telefone", "[TELEFONE]"),
    (TEL_SOLTO, "telefone", "[TELEFONE]"),
    (TEL_BARE, "telefone", "[TELEFONE]"),
]

NEGATIVOS_CLINICOS = [
    "Peso: 12,500 kg",
    "glicemia 413 mg/dl",
    "FC 130 bpm",
    "FR 40",
    "ECC 5/9",
    "atropina 0,04 mg/kg",
    "T 38,9",
    "consulta 2024-01-10",
    "plaquetas 200000-500000",
    "ureia 15-40",
    "VPM 7-11",
]


@pytest.mark.parametrize(("valor", "classe", "marcador"), POSITIVOS)
def test_positivo_e_redigido_e_detectado(valor: str, classe: str, marcador: str) -> None:
    texto = "contato " + valor + " fim"
    saida = scrub(texto, frozenset())
    assert valor not in saida
    assert marcador in saida
    assert varredura(texto) == [(classe, len("contato "))]


@pytest.mark.parametrize("texto", NEGATIVOS_CLINICOS)
def test_negativo_clinico_sobrevive(texto: str) -> None:
    assert scrub(texto, frozenset()) == texto
    assert varredura(texto) == []


def _texto_misto() -> str:
    return (
        "Tutor "
        + EMAIL_1
        + " empresa "
        + CNPJ_PONTUADO
        + " tel "
        + TEL_PAREN
        + " doc "
        + CPF_FALSO
        + "; Peso: 12,500 kg, glicemia 413 mg/dl, plaquetas 200000-500000, ECC 5/9."
    )


def test_idempotencia_com_todas_as_classes() -> None:
    uma_vez = scrub(_texto_misto(), frozenset())
    assert scrub(uma_vez, frozenset()) == uma_vez
    for marcador in ("[EMAIL]", "[CNPJ]", "[TELEFONE]", "[CPF]"):
        assert marcador in uma_vez
    assert "Peso: 12,500 kg" in uma_vez
    assert "plaquetas 200000-500000" in uma_vez


def test_varredura_nunca_devolve_o_valor() -> None:
    obj = {
        "a": ["x " + EMAIL_1, {"b": "cnpj " + CNPJ_PONTUADO}],
        "c": "tel " + TEL_PAREN + " cpf " + CPF_FALSO,
    }
    achados = varredura(obj)
    assert {classe for classe, _ in achados} == {"email", "cnpj", "telefone", "cpf"}
    saida = repr(achados)
    for valor in (EMAIL_1, CNPJ_PONTUADO, TEL_PAREN, CPF_FALSO):
        assert valor not in saida
    assert all(isinstance(pos, int) for _, pos in achados)


def test_celular_de_11_digitos_corridos_vira_cpf() -> None:
    # Ordem fixa: CPF antes do telefone. Redigido de qualquer forma.
    celular = "11" + "9" + "8765" + "4321"
    saida = scrub("tel " + celular, frozenset())
    assert celular not in saida
    assert "[CPF]" in saida
