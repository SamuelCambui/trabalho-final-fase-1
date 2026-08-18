"""
Setup automático do projeto Tech Challenge - Churn Prediction.

Fluxo:

1. Verifica Python
2. Verifica requirements.txt
3. Verifica/instala dependências
4. Localiza kaggle.json
5. Configura credenciais do Kaggle
6. Localiza o Kaggle CLI
7. Valida autenticação
8. Baixa o dataset
9. Extrai os arquivos
10. Valida os dados

Uso:

    python scripts/setup.py

Pré-requisito:

    Coloque o arquivo kaggle.json na raiz do projeto.

Estrutura esperada:

    tech-challenge-churn/
    ├── kaggle.json
    ├── requirements.txt
    ├── scripts/
    │   └── setup.py
    ├── data/
    └── ...
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
    print(f"[INFO] {message}")


def success(message: str) -> None:
    print(f"[OK] {message}")


def warning(message: str) -> None:
    print(f"[AVISO] {message}")


def error(message: str) -> None:
    print(f"[ERRO] {message}")


# ============================================================
# EXECUTAR COMANDO
# ============================================================

def run_command(
    command: list[str],
) -> subprocess.CompletedProcess[str]:

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

    version = sys.version_info

    info(
        f"Python encontrado: "
        f"{version.major}.{version.minor}.{version.micro}"
    )

    if version < MIN_PYTHON:

        error(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} "
            f"ou superior é necessário."
        )

        sys.exit(1)

    success("Versão do Python compatível.")


# ============================================================
# 2. REQUIREMENTS
# ============================================================

def install_requirements() -> None:

    requirements_file = PROJECT_ROOT / "requirements.txt"

    if not requirements_file.exists():

        error(
            "requirements.txt não encontrado."
        )

        sys.exit(1)

    info(
        "Instalando dependências do projeto..."
    )

    result = subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "-r",
            str(requirements_file),
        ],
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:

        error(
            "Falha ao instalar as dependências."
        )

        sys.exit(1)

    success(
        "Dependências instaladas."
    )


# ============================================================
# 3. KAGGLE JSON
# ============================================================

def configure_kaggle_credentials() -> None:

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
        f"Credenciais configuradas em:"
    )

    print(
        f"    {KAGGLE_CONFIG}"
    )


# ============================================================
# 4. LOCALIZAR KAGGLE CLI
# ============================================================

def find_kaggle_cli() -> Path | None:

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
# 5. VALIDAR KAGGLE
# ============================================================

def check_kaggle() -> Path:

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
            "Tente instalar novamente:"
        )

        print()
        print(
            f"{sys.executable} -m pip "
            "install --force-reinstall kaggle==2.2.4"
        )

        print()

        sys.exit(1)

    success(
        f"Kaggle encontrado:"
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

        print(
            result.stderr
        )

        sys.exit(1)

    success(
        f"Versão: {result.stdout.strip()}"
    )

    return kaggle


# ============================================================
# 6. VALIDAR AUTENTICAÇÃO
# ============================================================

def check_kaggle_authentication(
    kaggle: Path,
) -> None:

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
# 7. DIRETÓRIOS
# ============================================================

def create_directories() -> None:

    info(
        "Criando diretórios do projeto..."
    )

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    success(
        f"Diretório criado/verificado:"
    )

    print(
        f"    {RAW_DIR}"
    )


# ============================================================
# 8. DOWNLOAD DATASET
# ============================================================

def download_dataset(
    kaggle: Path,
) -> None:

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
# 9. EXTRAIR ZIP
# ============================================================

def extract_zip_files() -> None:

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
# 10. VALIDAR DATASET
# ============================================================

def validate_dataset() -> None:

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
            f"Diretório analisado:"
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
# 11. RESUMO
# ============================================================

def print_summary() -> None:

    print()
    print("=" * 60)
    print("SETUP CONCLUÍDO COM SUCESSO")
    print("=" * 60)

    print()
    print(
        "Projeto:"
    )

    print(
        f"    {PROJECT_ROOT}"
    )

    print()
    print(
        "Dataset:"
    )

    print(
        f"    {DATASET}"
    )

    print()
    print(
        "Dados:"
    )

    print(
        f"    {RAW_DIR}"
    )

    print()
    print(
        "Próximo passo:"
    )

    print(
        "    jupyter lab"
    )

    print()
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print()
    print("=" * 60)
    print("TECH CHALLENGE - CHURN PREDICTION")
    print("Setup automático do projeto")
    print("=" * 60)
    print()

    # 1
    check_python()

    # 2
    install_requirements()

    # 3
    configure_kaggle_credentials()

    # 4 e 5
    kaggle = check_kaggle()

    # 6
    check_kaggle_authentication(
        kaggle
    )

    # 7
    create_directories()

    # 8
    download_dataset(
        kaggle
    )

    # 9
    extract_zip_files()

    # 10
    validate_dataset()

    # 11
    print_summary()


if __name__ == "__main__":
    main()