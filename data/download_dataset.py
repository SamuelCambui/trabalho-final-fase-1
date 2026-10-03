import os
from pathlib import Path

from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env", override=False)

# Diretório onde o dataset original será armazenado
RAW_DATA_DIR = Path(os.getenv("DATA_DIR", "data/raw"))
if not RAW_DATA_DIR.is_absolute():
    RAW_DATA_DIR = PROJECT_ROOT / RAW_DATA_DIR

# Dataset do Kaggle
DATASET = os.getenv("KAGGLE_DATASET", "blastchar/telco-customer-churn")


def download_dataset() -> None:
    """
    Baixa o dataset de Churn do Kaggle e salva em data/raw.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    api = KaggleApi()
    api.authenticate()

    print("Baixando dataset do Kaggle...")

    api.dataset_download_files(
        DATASET,
        path=str(RAW_DATA_DIR),
        unzip=True
    )

    print(f"Dataset salvo em: {RAW_DATA_DIR}")


if __name__ == "__main__":
    download_dataset()
