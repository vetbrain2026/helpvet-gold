"""Invariantes de desenho do extrator (r1b-0.1). Esqueleto: sem parser real, so dado sintetico."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import helpvet_gold
from helpvet_gold import anotador_lexico, parsers_estruturais, quarentena, segmentacao
from helpvet_gold.anotador_lexico import Lexico, classificar_termo
from helpvet_gold.pii import scrub, varredura
from helpvet_gold.quarentena import FalhaQuarentena
from helpvet_gold.segmentacao import Bloco

SINTETICOS = Path(__file__).resolve().parent.parent / "fixtures" / "sinteticos"

# CPF fictício montado em tempo de execução (nunca literal no código).
CPF_FALSO = "111" + "." + "222" + "." + "333" + "-" + "44"


def _lexico() -> Lexico:
    abrev = json.loads((SINTETICOS / "lexico_abreviacoes.json").read_text(encoding="utf-8"))
    achados = json.loads((SINTETICOS / "lexico_achados.json").read_text(encoding="utf-8"))
    return Lexico(abreviacoes=abrev["abreviacoes"], achados=achados["achados"])


def _bloco() -> Bloco:
    return Bloco(id="B0001", tipo_bruto="Atendimento", carimbo="2030-01-10T09:30", texto="x")


def test_versao_do_extrator() -> None:
    assert helpvet_gold.__version__ == "0.1.0"


def test_lexicos_sao_marcados_como_semente() -> None:
    for nome in ("lexico_abreviacoes.json", "lexico_achados.json"):
        dados = json.loads((SINTETICOS / nome).read_text(encoding="utf-8"))
        assert "SEMENTE" in dados["_aviso"]


@pytest.mark.parametrize(
    "frase",
    [
        "Paciente com tosse ha dois dias.",
        "Tutor informou o documento " + CPF_FALSO + " na recepcao.",
        "Sem alteracoes; " + CPF_FALSO + " e " + CPF_FALSO,
        "",
    ],
)
def test_scrub_e_idempotente(frase: str) -> None:
    uma_vez = scrub(frase, frozenset())
    assert scrub(uma_vez, frozenset()) == uma_vez


def test_scrub_remove_cpf() -> None:
    assert CPF_FALSO not in scrub("doc " + CPF_FALSO, frozenset())


def test_varredura_acha_cpf_e_nunca_devolve_o_valor() -> None:
    obj = {"eventos": [{"trecho": "doc " + CPF_FALSO}]}
    achados = varredura(obj)
    assert achados == [("cpf", 4)]
    assert CPF_FALSO not in repr(achados)


def test_varredura_nao_acha_nada_em_texto_limpo() -> None:
    assert varredura({"a": ["mucosas normocoradas", 3, None]}) == []


def test_abreviacao_fora_do_lexico_vai_para_quarentena() -> None:
    lexico = _lexico()
    assert classificar_termo("zzq", lexico) == "termo_fora_do_lexico"
    assert classificar_termo("hipoc", lexico) is None
    assert classificar_termo("tosse", lexico) is None


@pytest.mark.parametrize(
    "chamada",
    [
        lambda: segmentacao.segmentar("x"),
        lambda: parsers_estruturais.parse_paciente("x"),
        lambda: parsers_estruturais.parse_medidas(_bloco()),
        lambda: parsers_estruturais.parse_receita(_bloco()),
        lambda: parsers_estruturais.parse_formulario(_bloco()),
        lambda: parsers_estruturais.parse_datas(_bloco()),
        lambda: anotador_lexico.anotar(_bloco(), _lexico()),
        lambda: anotador_lexico.varredura_obrigatoria(_bloco(), _lexico()),
        lambda: quarentena.registrar(
            FalhaQuarentena("p", "B0001", "pii_detectada", "classe=cpf, contagem=1", 1, None, "x")
        ),
    ],
)
def test_pontos_pendentes_nao_fingem_implementacao(chamada: object) -> None:
    assert callable(chamada)
    with pytest.raises(NotImplementedError):
        chamada()
