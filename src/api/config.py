"""Configurações da API de predição de churn."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

API_TITLE = "Customer Churn Prediction API"
API_DESCRIPTION = (
    "API para previsão de churn de clientes Telco "
    "(modelo campeão: Logistic Regression, notebook de modelagem)."
)
API_VERSION = "1.1.0"

# Artefato do notebook modelagem_avaliacao_churn_prediction.ipynb
CHAMPION_MODEL_PATH = (
    PROJECT_ROOT / "notebooks" / "models" / "champion_model.joblib"
)
MODEL_PATH: Path = Path(
    os.getenv("MODEL_PATH", str(CHAMPION_MODEL_PATH))
)

PREDICTION_THRESHOLD = 0.5
PROBABILITY_DECIMALS = 4

JWT_SECRET_KEY = os.getenv("SECRET_KEY", "altere-esta-chave-em-producao")
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

USERS_DB = {
    "admin": {"password": "admin", "role": "admin"},
    "user": {"password": "user", "role": "user"},
}
