"""Recusa arquivos fora da lista de caminhos permitidos.

Uso: python scripts/check_allowed_paths.py ARQUIVO [ARQUIVO ...]

Sai com código 1 se algum arquivo está fora da lista. Imprime só o caminho.
"""

from __future__ import annotations

import sys
from pathlib import PurePosixPath

ALLOWED_DIRS: tuple[str, ...] = (
    "src",
    "tests",
    "scripts",
    "docs",
    "contrato",
    "fixtures/sinteticos",
    ".github",
)

ALLOWED_ROOT_FILES: frozenset[str] = frozenset(
    {
        "pyproject.toml",
        "uv.lock",
        ".gitignore",
        ".gitleaks.toml",
        ".pre-commit-config.yaml",
        "README.md",
        "CLAUDE.md",
        "KNOWN_ISSUES.md",
    }
)


def is_allowed(path: str) -> bool:
    normalized = PurePosixPath(path.replace("\\", "/"))
    parts = normalized.parts
    if not parts or normalized.is_absolute() or ".." in parts:
        return False
    if len(parts) == 1:
        return parts[0] in ALLOWED_ROOT_FILES
    for directory in ALLOWED_DIRS:
        dir_parts = PurePosixPath(directory).parts
        if len(parts) > len(dir_parts) and parts[: len(dir_parts)] == dir_parts:
            return True
    return False


def main(argv: list[str]) -> int:
    failed = False
    for name in argv:
        if not is_allowed(name):
            print(f"{name}: caminho fora da lista de permitidos")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
