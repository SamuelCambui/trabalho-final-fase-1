"""Configurações da API de predição de churn."""

import os
from pathlib import Path

from src.environment import PROJECT_ROOT, project_path

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
MODEL_PATH: Path = project_path("MODEL_PATH", str(CHAMPION_MODEL_PATH))

PREDICTION_THRESHOLD = float(os.getenv("PREDICTION_THRESHOLD", "0.5"))
PROBABILITY_DECIMALS = int(os.getenv("PROBABILITY_DECIMALS", "4"))

JWT_SECRET_KEY = os.environ["SECRET_KEY"]
if not JWT_SECRET_KEY or JWT_SECRET_KEY == "altere-esta-chave-em-producao":
    raise ValueError("Configure SECRET_KEY no .env ou no ambiente.")
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

USERS_DB = {}
for prefix, role in (("API_ADMIN", "admin"), ("API_USER", "user")):
    username = os.getenv(f"{prefix}_USERNAME")
    password = os.getenv(f"{prefix}_PASSWORD")
    if username and password:
        USERS_DB[username] = {"password": password, "role": role}
