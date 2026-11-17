"""Valida o esquema do contrato 1.2 e o exemplo sintetico contra ele."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

RAIZ = Path(__file__).resolve().parent.parent
ESQUEMA = RAIZ / "contrato" / "helpvet-gold-1.2.schema.json"
EXEMPLO = RAIZ / "fixtures" / "sinteticos" / "exemplo_ouro.json"


def _carregar(caminho: Path) -> Any:
    return json.loads(caminho.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validador() -> Draft202012Validator:
    esquema = _carregar(ESQUEMA)
    Draft202012Validator.check_schema(esquema)
    return Draft202012Validator(esquema)


@pytest.fixture
def exemplo() -> Any:
    return _carregar(EXEMPLO)


def test_exemplo_valida(validador: Draft202012Validator, exemplo: Any) -> None:
    erros = [e.message for e in validador.iter_errors(exemplo)]
    assert erros == []


def test_exemplo_cobre_campos_novos(exemplo: Any) -> None:
    medidas = [m["tipo"] for ev in exemplo["eventos"] for m in ev["medidas"]]
    achados = [a["achado_tipo"] for ev in exemplo["eventos"] for a in ev["achados"]]
    procs = [p["categoria"] for ev in exemplo["eventos"] for p in ev["procedimentos"]]
    assert "tpc" in medidas
    assert {"mucosas", "linfonodos"} <= set(achados)
    assert "medicacao_administrada" in procs


def test_grupo_tutor_ref_diferente_de_null_e_recusado(
    validador: Draft202012Validator, exemplo: Any
) -> None:
    ruim = copy.deepcopy(exemplo)
    ruim["paciente"]["grupo_tutor_ref"] = "g1"
    assert not validador.is_valid(ruim)


def test_item_clinico_sem_trecho_e_recusado(validador: Draft202012Validator, exemplo: Any) -> None:
    ruim = copy.deepcopy(exemplo)
    del ruim["eventos"][0]["medidas"][0]["trecho"]
    assert not validador.is_valid(ruim)


def test_trecho_nulo_e_recusado(validador: Draft202012Validator, exemplo: Any) -> None:
    ruim = copy.deepcopy(exemplo)
    ruim["eventos"][1]["exames"][0]["trecho"] = None
    assert not validador.is_valid(ruim)


def test_campo_extra_e_recusado(validador: Draft202012Validator, exemplo: Any) -> None:
    ruim = copy.deepcopy(exemplo)
    ruim["eventos"][0]["problema"] = "x"
    assert not validador.is_valid(ruim)


def test_campos_1_1_removidos_sao_recusados(validador: Draft202012Validator, exemplo: Any) -> None:
    ruim = copy.deepcopy(exemplo)
    ruim["extracao"]["modelo_1b"] = "x"
    assert not validador.is_valid(ruim)
