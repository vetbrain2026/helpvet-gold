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


CPF_SOLTO = "123456" + "78909"
CNPJ_SOLTO = "12345678" + "000195"
TEL10_SOLTO = "1198765" + "4321"
TEL11_SOLTO = "11987" + "654321"


@pytest.mark.parametrize(
    ("valor", "tipo"),
    [
        (CPF_SOLTO, "CPF_SEM_PONTUACAO"),
        (CNPJ_SOLTO, "CNPJ_SEM_PONTUACAO"),
        (TEL10_SOLTO, "TELEFONE_SEM_PONTUACAO"),
        (TEL11_SOLTO, "TELEFONE_SEM_PONTUACAO"),
    ],
)
def test_sequencia_numerica_solta_e_barrada(valor: str, tipo: str) -> None:
    achados = check_pii_patterns.find_pii("ok\nnumero " + valor + " fim\n")
    assert (2, tipo) in achados


@pytest.mark.parametrize("valor", ["123456789", "123456789012", "123456789012345", "42"])
def test_numeros_de_outros_tamanhos_passam(valor: str) -> None:
    assert check_pii_patterns.find_pii("n " + valor) == []


def test_somente_uv_lock_e_isento(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    Path("uv.lock").write_text("size = " + CPF_SOLTO + "\n", encoding="utf-8")
    Path("outro.lock").write_text("size = " + CPF_SOLTO + "\n", encoding="utf-8")
    assert check_pii_patterns.main(["uv.lock"]) == 0
    assert check_pii_patterns.main(["outro.lock"]) == 1
    saida = capsys.readouterr().out
    assert "outro.lock:1:" in saida
    assert CPF_SOLTO not in saida


def test_cp1252_com_acento_e_recusado(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    arquivo = tmp_path / "cp1252.txt"
    arquivo.write_bytes("coração".encode("cp1252"))
    assert check_pii_patterns.main([str(arquivo)]) == 1
    assert capsys.readouterr().out.strip() == f"{arquivo}: não é UTF-8"


def test_bytes_com_nul_sao_recusados(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    arquivo = tmp_path / "bin.txt"
    arquivo.write_bytes(b"abc\x00def")
    assert check_pii_patterns.main([str(arquivo)]) == 1
    assert "arquivo binário ou UTF-16 não permitido" in capsys.readouterr().out


def test_utf16_e_recusado(tmp_path: Path) -> None:
    arquivo = tmp_path / "u16.txt"
    arquivo.write_bytes("texto".encode("utf-16"))
    assert check_pii_patterns.main([str(arquivo)]) == 1


def test_arquivo_ilegivel_e_recusado(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    inexistente = tmp_path / "nao_existe.txt"
    assert check_pii_patterns.main([str(inexistente)]) == 1
    assert capsys.readouterr().out.strip() == f"{inexistente}: ilegível"


def test_utf8_limpo_com_acento_e_aceito(tmp_path: Path) -> None:
    arquivo = tmp_path / "ok.txt"
    arquivo.write_text("coração e ação", encoding="utf-8")
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


@pytest.mark.parametrize("pasta", ["fixtures/sinteticos", "contrato"])
def test_limite_de_100_kb(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    pasta: str,
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / pasta).mkdir(parents=True)
    Path(pasta, "ok.json").write_bytes(b"a" * (100 * 1024))
    Path(pasta, "grande.json").write_bytes(b"a" * (100 * 1024 + 1))
    assert check_allowed_paths.main([f"{pasta}/ok.json"]) == 0
    assert check_allowed_paths.main([f"{pasta}/grande.json"]) == 1
    assert capsys.readouterr().out.strip() == f"{pasta}/grande.json: acima de 100 KB"


def test_main_caminhos() -> None:
    assert check_allowed_paths.main(["README.md"]) == 0
    assert check_allowed_paths.main(["README.md", "anotacoes.txt"]) == 1
