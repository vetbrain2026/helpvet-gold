"""Verificador determinístico de padrões de PII (CPF, CNPJ, telefone BR, e-mail).

Uso: python scripts/check_pii_patterns.py ARQUIVO [ARQUIVO ...]

Sai com código 1 se algum arquivo contém um padrão. Imprime só arquivo, linha e
tipo do achado, nunca o valor.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS: dict[str, re.Pattern[str]] = {
    "CPF": re.compile(r"(?<!\d)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\d)"),
    "CNPJ": re.compile(r"(?<!\d)\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}(?!\d)"),
    "TELEFONE": re.compile(
        r"(?<!\d)(?:\+55\s?)?(?:\(\d{2}\)\s?|\d{2}\s)9?\d{4}-?\d{4}(?!\d)"
        r"|(?<!\d)9?\d{4}-\d{4}(?!\d)"
    ),
    "EMAIL": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"),
}


def find_pii(text: str) -> list[tuple[int, str]]:
    """Devolve (linha, tipo) de cada achado, sem expor o valor."""
    findings: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append((number, kind))
    return findings


def main(argv: list[str]) -> int:
    failed = False
    for name in argv:
        path = Path(name)
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, kind in find_pii(text):
            print(f"{name}:{number}: padrão de {kind} encontrado")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
