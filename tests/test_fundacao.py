"""Testes da fundação: pacote, verificador de PII e verificador de caminhos.

As strings fictícias de PII são montadas em tempo de execução, por concatenação
de pedaços que sozinhos não casam o padrão, para este arquivo passar nos
verificadores e no gitleaks.
"""

from pathlib import Path

import pytest

import helpvet_gold
from scripts import check_allowed_paths, check_pii_patterns

CPF = "123" + "." + "456" + "." + "789" + "-" + "09"
CNPJ = "12" + "." + "345" + "." + "678" + "/" + "0001" + "-" + "95"
TELEFONE = "(" + "11" + ") " + "98765" + "-" + "4321"
EMAIL = "fulano" + "@" + "exemplo" + "." + "com"
LIMPO = "Paciente canino fictício, 12 kg, retorno em 3 dias."


def test_versao_do_pacote() -> None:
    assert helpvet_gold.__version__ == "0.0.0"


def test_texto_limpo_passa() -> None:
    assert check_pii_patterns.find_pii(LIMPO) == []


@pytest.mark.parametrize(
    ("valor", "tipo"),
    [(CPF, "CPF"), (CNPJ, "CNPJ"), (TELEFONE, "TELEFONE"), (EMAIL, "EMAIL")],
)
def test_pii_e_barrado(valor: str, tipo: str) -> None:
    achados = check_pii_patterns.find_pii("linha limpa\nvalor: " + valor + "\n")
    assert (2, tipo) in achados


def test_main_pii_nao_imprime_valor(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    arquivo = tmp_path / "sujo.txt"
    arquivo.write_text("x " + CPF + "\n", encoding="utf-8")
    assert check_pii_patterns.main([str(arquivo)]) == 1
    saida = capsys.readouterr().out
    assert "CPF" in saida
    assert CPF not in saida


def test_main_pii_limpo(tmp_path: Path) -> None:
    arquivo = tmp_path / "limpo.txt"
    arquivo.write_text(LIMPO, encoding="utf-8")
    assert check_pii_patterns.main([str(arquivo)]) == 0


def test_este_arquivo_passa_no_verificador() -> None:
    assert check_pii_patterns.main([__file__]) == 0


@pytest.mark.parametrize(
    "caminho",
    [
        "src/helpvet_gold/__init__.py",
        "tests/test_fundacao.py",
        "scripts/check_pii_patterns.py",
        "docs/DECISOES.md",
        "contrato/README.md",
        "fixtures/sinteticos/README.md",
        ".github/workflows/ci.yml",
        "pyproject.toml",
        "uv.lock",
        ".gitignore",
        ".gitleaks.toml",
        ".pre-commit-config.yaml",
        "README.md",
        "CLAUDE.md",
        "KNOWN_ISSUES.md",
        ".gitattributes",
        "fixtures/sinteticos/x.md",
        "contrato/x.json",
    ],
)
def test_caminho_permitido(caminho: str) -> None:
    assert check_allowed_paths.is_allowed(caminho)


@pytest.mark.parametrize(
    "caminho",
    [
        "anotacoes.txt",
        "fixtures/outro/a.txt",
        "fixtures/a.txt",
        "data/x.json",
        "src",
        "../fora.txt",
        "docs/../segredo.txt",
        "docs/x.txt",
        "src/x.json",
        "scripts/x.md",
        "contrato/x.txt",
        "fixtures/sinteticos/x.pdf",
        ".github/x.json",
    ],
)
def test_caminho_recusado(caminho: str) -> None:
    assert not check_allowed_paths.is_allowed(caminho)


def test_motivo_de_extensao_sem_valor(capsys: pytest.CaptureFixture[str]) -> None:
    assert check_allowed_paths.main(["docs/x.txt"]) == 1
    assert capsys.readouterr().out.strip() == "docs/x.txt: extensão não permitida em docs/"


def test_main_caminhos() -> None:
    assert check_allowed_paths.main(["README.md"]) == 0
    assert check_allowed_paths.main(["README.md", "anotacoes.txt"]) == 1
