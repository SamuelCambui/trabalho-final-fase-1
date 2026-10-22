"""Shared environment loading; exported variables take precedence over .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)


def project_path(name: str, default: str) -> Path:
    """Resolve um caminho configurável via variável de ambiente.

    Caminhos relativos são resolvidos a partir da raiz do projeto, não
    do diretório de trabalho atual — assim o resultado não muda
    dependendo de onde o comando foi executado.

    Args:
        name: Nome da variável de ambiente (ex.: ``"MODEL_PATH"``).
        default: Valor usado se a variável não estiver definida.

    Returns:
        Caminho absoluto, relativo à raiz do projeto quando aplicável.
    """
    path = Path(os.getenv(name, default)).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path
