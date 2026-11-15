"""Recusa arquivos fora da lista de caminhos e extensões permitidos.

Uso: python scripts/check_allowed_paths.py ARQUIVO [ARQUIVO ...]

Sai com código 1 se algum arquivo está fora da lista. Imprime só arquivo e motivo.
"""

from __future__ import annotations

import sys
from pathlib import Path, PurePosixPath

ALLOWED_DIRS: dict[str, frozenset[str]] = {
    "src": frozenset({".py"}),
    "tests": frozenset({".py"}),
    "scripts": frozenset({".py"}),
    "docs": frozenset({".md"}),
    "contrato": frozenset({".md", ".json"}),
    "fixtures/sinteticos": frozenset({".md", ".txt", ".json"}),
    ".github": frozenset({".yml", ".yaml"}),
}

ALLOWED_ROOT_FILES: frozenset[str] = frozenset(
    {
        "pyproject.toml",
        "uv.lock",
        ".gitignore",
        ".gitattributes",
        ".gitleaks.toml",
        ".pre-commit-config.yaml",
        "README.md",
        "CLAUDE.md",
        "KNOWN_ISSUES.md",
    }
)


SIZE_LIMITED_DIRS: frozenset[str] = frozenset({"fixtures/sinteticos", "contrato"})
MAX_BYTES = 100 * 1024


def _size(path: str) -> int:
    try:
        return Path(path).stat().st_size
    except OSError:
        return 0


def check_path(path: str) -> str | None:
    """Devolve o motivo da recusa, ou None se o caminho é permitido."""
    normalized = PurePosixPath(path.replace("\\", "/"))
    parts = normalized.parts
    if not parts or normalized.is_absolute() or ".." in parts:
        return "caminho inválido"
    if len(parts) == 1:
        if parts[0] in ALLOWED_ROOT_FILES:
            return None
        return "arquivo de raiz fora da lista de permitidos"
    for directory, extensions in ALLOWED_DIRS.items():
        dir_parts = PurePosixPath(directory).parts
        if len(parts) > len(dir_parts) and parts[: len(dir_parts)] == dir_parts:
            if normalized.suffix in extensions:
                if directory in SIZE_LIMITED_DIRS and _size(path) > MAX_BYTES:
                    return "acima de 100 KB"
                return None
            return f"extensão não permitida em {directory}/"
    return "pasta fora da lista de permitidas"


def is_allowed(path: str) -> bool:
    return check_path(path) is None


def main(argv: list[str]) -> int:
    failed = False
    for name in argv:
        reason = check_path(name)
        if reason is not None:
            print(f"{name}: {reason}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
