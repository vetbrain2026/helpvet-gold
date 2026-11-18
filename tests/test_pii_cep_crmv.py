"""Camadas CEP e CRMV da PII. So dado sintetico, montado em runtime."""

from __future__ import annotations

import pytest

from helpvet_gold.pii import scrub, varredura

CEP_FALSO = "12345" + "-" + "678"
CRMV_1 = "CRMV" + "-SP " + "12345"
CRMV_2 = "CRMV" + "/SP " + "98765"
CRMV_3 = "CRMV" + " SP " + "12345"
CRMV_4 = "CRMV" + "-SP nº " + "12345"
CRMV_MINUSCULO = "crmv" + "-sp " + "12345"

POSITIVOS = [
    (CEP_FALSO, "cep", "[CEP]"),
    (CRMV_1, "crmv", "[CRMV]"),
    (CRMV_2, "crmv", "[CRMV]"),
    (CRMV_3, "crmv", "[CRMV]"),
    (CRMV_4, "crmv", "[CRMV]"),
    (CRMV_MINUSCULO, "crmv", "[CRMV]"),
]

NEGATIVOS = [
    "protocolo 20240110",
    "consulta 2024-01-10",
    "ureia 15-40",
    "VPM 7-11",
    "plaquetas 200000-500000",
    "Peso: 12,500 kg",
    "ECC 5/9",
]


@pytest.mark.parametrize(("valor", "classe", "marcador"), POSITIVOS)
def test_positivo_e_redigido_e_detectado(valor: str, classe: str, marcador: str) -> None:
    texto = "dado " + valor + " fim"
    saida = scrub(texto, frozenset())
    assert valor not in saida
    assert saida == "dado " + marcador + " fim"
    assert varredura(texto) == [(classe, len("dado "))]


@pytest.mark.parametrize("texto", NEGATIVOS)
def test_negativo_sobrevive(texto: str) -> None:
    assert scrub(texto, frozenset()) == texto
    assert varredura(texto) == []


def test_idempotencia_com_cep_e_crmv() -> None:
    texto = "Atendido por " + CRMV_1 + ", end. " + CEP_FALSO + "; Peso: 12,500 kg, ureia 15-40."
    uma_vez = scrub(texto, frozenset())
    assert scrub(uma_vez, frozenset()) == uma_vez
    assert "[CEP]" in uma_vez
    assert "[CRMV]" in uma_vez
    assert "Peso: 12,500 kg" in uma_vez
    assert "ureia 15-40" in uma_vez


def test_varredura_nunca_devolve_o_valor() -> None:
    obj = {"a": ["x " + CEP_FALSO], "b": {"c": "y " + CRMV_1}}
    achados = varredura(obj)
    assert {classe for classe, _ in achados} == {"cep", "crmv"}
    assert all(isinstance(pos, int) for _, pos in achados)
    saida = repr(achados)
    assert CEP_FALSO not in saida
    assert CRMV_1 not in saida
    assert "12345" not in saida
