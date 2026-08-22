"""
Setup automático do projeto Tech Challenge - Churn Prediction.

Fluxo:

1. Verifica Python
2. Verifica pyproject.toml
3. Instala as dependências do projeto através do pyproject.toml
4. Localiza kaggle.json
5. Configura credenciais do Kaggle
6. Localiza o Kaggle CLI
7. Valida autenticação
8. Cria os diretórios necessários
9. Baixa o dataset
10. Extrai os arquivos
11. Valida os dados

Uso:

    python scripts/setup.py

Pré-requisito:

    Coloque o arquivo kaggle.json na raiz do projeto.

Estrutura esperada:

    trabalho-final-fase-1/
    ├── kaggle.json
    ├── pyproject.toml
    ├── scripts/
    │   └── setup.py
    ├── data/
    └── src/
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import sysconfig
import zipfile
from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PYPROJECT_FILE = PROJECT_ROOT / "pyproject.toml"

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"

KAGGLE_JSON = PROJECT_ROOT / "kaggle.json"

KAGGLE_DIR = Path.home() / ".kaggle"
KAGGLE_CONFIG = KAGGLE_DIR / "kaggle.json"

# Dataset IBM Telco Customer Churn
DATASET = "blastchar/telco-customer-churn"

MIN_PYTHON = (3, 11)


# ============================================================
# LOG
# ============================================================

def info(message: str) -> None:
    """Exibe uma mensagem informativa."""
    print(f"[INFO] {message}")


def success(message: str) -> None:
    """Exibe uma mensagem de sucesso."""
    print(f"[OK] {message}")


def warning(message: str) -> None:
    """Exibe uma mensagem de aviso."""
    print(f"[AVISO] {message}")


def error(message: str) -> None:
    """Exibe uma mensagem de erro."""
    print(f"[ERRO] {message}")


# ============================================================
# EXECUTAR COMANDO
# ============================================================

def run_command(
    command: list[str],
) -> subprocess.CompletedProcess[str]:
    """Executa um comando no diretório raiz do projeto."""

    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


# ============================================================
# 1. PYTHON
# ============================================================

def check_python() -> None:
    """Verifica se a versão do Python é compatível."""

    version = sys.version_info

    info(
        f"Python encontrado: "
        f"{version.major}.{version.minor}.{version.micro}"
    )

    if version < MIN_PYTHON:
        error(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} "
            "ou superior é necessário."
        )

        sys.exit(1)

    success("Versão do Python compatível.")


# ============================================================
# 2. PYPROJECT.TOML
# ============================================================

def check_pyproject() -> None:
    """Verifica se o pyproject.toml existe."""

    info("Verificando pyproject.toml...")

    if not PYPROJECT_FILE.exists():
        error(
            "pyproject.toml não encontrado."
        )

        print()
        print(
            "O arquivo deve estar na raiz do projeto:"
        )

        print()
        print(
            f"    {PYPROJECT_FILE}"
        )

        print()

        sys.exit(1)

    success(
        "pyproject.toml encontrado."
    )


# ============================================================
# 3. INSTALAR DEPENDÊNCIAS
# ============================================================

def install_project() -> None:
    """
    Instala o projeto e suas dependências utilizando
    exclusivamente o pyproject.toml.
    """

    info(
        "Instalando o projeto e suas dependências..."
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-e",
            ".",
        ],
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        error(
            "Falha ao instalar o projeto ou suas dependências."
        )

        print()
        print(
            "Verifique as dependências definidas no "
            "pyproject.toml."
        )

        print()

        sys.exit(1)

    success(
        "Projeto e dependências instalados com sucesso."
    )


# ============================================================
# 4. KAGGLE JSON
# ============================================================

def configure_kaggle_credentials() -> None:
    """Configura as credenciais do Kaggle."""

    info(
        "Procurando kaggle.json..."
    )

    if not KAGGLE_JSON.exists():
        error(
            "Arquivo kaggle.json não encontrado."
        )

        print()
        print(
            "Coloque seu kaggle.json na raiz do projeto:"
        )

        print()
        print(
            f"    {KAGGLE_JSON}"
        )

        print()
        print(
            "O arquivo pode ser obtido nas configurações "
            "da sua conta do Kaggle."
        )

        print()
        print(
            "Acesse:"
        )

        print(
            "    https://www.kaggle.com/settings/api"
        )

        print()

        sys.exit(1)

    success(
        "kaggle.json encontrado."
    )

    # Criar ~/.kaggle
    KAGGLE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Copiar credencial
    shutil.copy2(
        KAGGLE_JSON,
        KAGGLE_CONFIG,
    )

    # Linux/macOS
    if os.name != "nt":
        try:
            KAGGLE_CONFIG.chmod(0o600)

        except OSError:
            warning(
                "Não foi possível alterar as permissões "
                "do kaggle.json."
            )

    success(
        "Credenciais do Kaggle configuradas."
    )

    print(
        f"    {KAGGLE_CONFIG}"
    )


# ============================================================
# 5. LOCALIZAR KAGGLE CLI
# ============================================================

def find_kaggle_cli() -> Path | None:
    """
    Localiza o executável do Kaggle CLI.

    Procura:

    1. PATH do sistema
    2. Diretório Scripts do Python atual
    3. Instalações do Python da Microsoft Store no Windows
    """

    # --------------------------------------------------------
    # 1. PATH
    # --------------------------------------------------------

    kaggle = shutil.which("kaggle")

    if kaggle:
        return Path(kaggle)

    # --------------------------------------------------------
    # 2. Scripts do Python atual
    # --------------------------------------------------------

    scripts_dir = Path(
        sysconfig.get_path("scripts")
    )

    candidates = [
        scripts_dir / "kaggle",
        scripts_dir / "kaggle.exe",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # --------------------------------------------------------
    # 3. Windows / Microsoft Store
    # --------------------------------------------------------

    if os.name == "nt":
        local_app_data = os.environ.get(
            "LOCALAPPDATA"
        )

        if local_app_data:
            packages_dir = (
                Path(local_app_data)
                / "Packages"
            )

            if packages_dir.exists():
                for candidate in packages_dir.glob(
                    "*/LocalCache/local-packages/"
                    "Python*/Scripts/kaggle.exe"
                ):
                    if candidate.exists():
                        return candidate

    return None


# ============================================================
# 6. VALIDAR KAGGLE
# ============================================================

def check_kaggle() -> Path:
    """Localiza e valida o Kaggle CLI."""

    info(
        "Localizando Kaggle CLI..."
    )

    kaggle = find_kaggle_cli()

    if kaggle is None:
        error(
            "Kaggle CLI não encontrado."
        )

        print()
        print(
            "O pacote 'kaggle' deve estar definido "
            "nas dependências do pyproject.toml."
        )

        print()
        print(
            "Tente executar:"
        )

        print()
        print(
            f"{sys.executable} -m pip install -e ."
        )

        print()

        sys.exit(1)

    success(
        "Kaggle CLI encontrado:"
    )

    print(
        f"    {kaggle}"
    )

    # --------------------------------------------------------
    # Versão
    # --------------------------------------------------------

    result = run_command(
        [
            str(kaggle),
            "--version",
        ]
    )

    if result.returncode != 0:
        error(
            "Kaggle CLI foi encontrado, "
            "mas não pode ser executado."
        )

        if result.stderr:
            print(
                result.stderr
            )

        sys.exit(1)

    success(
        f"Versão: {result.stdout.strip()}"
    )

    return kaggle


# ============================================================
# 7. VALIDAR AUTENTICAÇÃO
# ============================================================

def check_kaggle_authentication(
    kaggle: Path,
) -> None:
    """Valida a autenticação da API do Kaggle."""

    info(
        "Validando autenticação do Kaggle..."
    )

    result = run_command(
        [
            str(kaggle),
            "datasets",
            "list",
            "--max-size",
            "1",
        ]
    )

    if result.returncode == 0:
        success(
            "Autenticação do Kaggle validada."
        )

        return

    error(
        "Falha na autenticação do Kaggle."
    )

    print()

    if result.stderr:
        print(
            result.stderr
        )

    print()
    print(
        "Verifique se o arquivo kaggle.json é válido."
    )

    sys.exit(1)


# ============================================================
# 8. DIRETÓRIOS
# ============================================================

def create_directories() -> None:
    """Cria os diretórios necessários para os dados."""

    info(
        "Criando diretórios do projeto..."
    )

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    success(
        "Diretório criado/verificado:"
    )

    print(
        f"    {RAW_DIR}"
    )


# ============================================================
# 9. DOWNLOAD DATASET
# ============================================================

def download_dataset(
    kaggle: Path,
) -> None:
    """Baixa o dataset do Kaggle."""

    info(
        f"Baixando dataset: {DATASET}"
    )

    command = [
        str(kaggle),
        "datasets",
        "download",
        "-d",
        DATASET,
        "-p",
        str(RAW_DIR),
        "--unzip",
    ]

    result = run_command(
        command
    )

    if result.returncode != 0:
        error(
            "Falha ao baixar o dataset."
        )

        if result.stderr:
            print(
                result.stderr
            )

        sys.exit(1)

    success(
        "Dataset baixado com sucesso."
    )


# ============================================================
# 10. EXTRAIR ZIP
# ============================================================

def extract_zip_files() -> None:
    """Extrai arquivos ZIP encontrados em data/raw."""

    zip_files = list(
        RAW_DIR.glob("*.zip")
    )

    if not zip_files:
        return

    info(
        f"{len(zip_files)} arquivo(s) ZIP encontrado(s)."
    )

    for zip_file in zip_files:
        info(
            f"Extraindo {zip_file.name}..."
        )

        with zipfile.ZipFile(
            zip_file,
            "r",
        ) as zip_ref:
            zip_ref.extractall(
                RAW_DIR
            )

        success(
            f"{zip_file.name} extraído."
        )


# ============================================================
# 11. VALIDAR DATASET
# ============================================================

def validate_dataset() -> None:
    """Valida a existência dos arquivos CSV."""

    info(
        "Validando arquivos do dataset..."
    )

    csv_files = list(
        RAW_DIR.glob("*.csv")
    )

    if not csv_files:
        error(
            "Nenhum arquivo CSV foi encontrado."
        )

        print()
        print(
            "Diretório analisado:"
        )

        print(
            f"    {RAW_DIR}"
        )

        sys.exit(1)

    success(
        f"{len(csv_files)} arquivo(s) CSV encontrado(s)."
    )

    for csv_file in csv_files:
        print(
            f"    └── {csv_file.name}"
        )


# ============================================================
# 12. RESUMO
# ============================================================

def print_summary() -> None:
    """Exibe o resumo da execução do setup."""

    print()
    print("=" * 60)
    print("SETUP CONCLUÍDO COM SUCESSO")
    print("=" * 60)

    print()
    print("Projeto:")

    print(
        f"    {PROJECT_ROOT}"
    )

    print()
    print("Dataset:")

    print(
        f"    {DATASET}"
    )

    print()
    print("Dados:")

    print(
        f"    {RAW_DIR}"
    )

    print()
    print("Próximo passo:")

    print(
        "    python -m src.train_model.train"
    )

    print()
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Executa o processo completo de configuração."""

    print()
    print("=" * 60)
    print("TECH CHALLENGE - CHURN PREDICTION")
    print("Setup automático do projeto")
    print("=" * 60)
    print()

    # 1. Python
    check_python()

    # 2. pyproject.toml
    check_pyproject()

    # 3. Dependências
    install_project()

    # 4. Credenciais Kaggle
    configure_kaggle_credentials()

    # 5. Kaggle CLI
    kaggle = check_kaggle()

    # 6. Autenticação
    check_kaggle_authentication(
        kaggle
    )

    # 7. Diretórios
    create_directories()

    # 8. Download
    download_dataset(
        kaggle
    )

    # 9. Extração
    extract_zip_files()

    # 10. Validação
    validate_dataset()

    # 11. Resumo
    print_summary()


if __name__ == "__main__":
    main()

