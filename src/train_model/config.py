"""Constantes e hiperparâmetros do pipeline de treinamento."""

import json
import os

from src.environment import PROJECT_ROOT as PROJECT_ROOT
from src.environment import project_path

DATA_DIR = project_path("DATA_DIR", "data/raw")
MODELS_DIR = project_path("MODELS_DIR", "models")

TARGET_COLUMN = os.getenv("TARGET_COLUMN", "Churn")
ID_COLUMN = os.getenv("ID_COLUMN", "customerID")
RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))
TEST_SIZE = float(os.getenv("TEST_SIZE", "0.3"))
CV_FOLDS = int(os.getenv("CV_FOLDS", "5"))
SCORING = os.getenv("SCORING", "roc_auc")

RF_MODEL_PATH = MODELS_DIR / "rf_model.joblib"
MLP_MODEL_PATH = MODELS_DIR / "mlp_model.joblib"
BEST_MODEL_PATH = MODELS_DIR / "model.joblib"
COMPARISON_REPORT_PATH = MODELS_DIR / "comparison_results.csv"

RF_PARAM_GRID = {
    "classifier__n_estimators": [100, 200, 300],
    "classifier__max_depth": [None, 10, 20],
    "classifier__min_samples_split": [2, 5, 10],
}

MLP_PARAM_GRID = {
    "classifier__hidden_layer_sizes": [(50,), (100,), (64, 32)],
    "classifier__activation": ["relu", "tanh"],
    "classifier__alpha": [0.0001, 0.001, 0.01],
}

# ==========================================================
# MLflow (tracking do pipeline de treino automatizado / CI)
# ==========================================================
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "churn-prediction-cicd")
MODEL_REGISTRY_NAME = os.getenv("MODEL_REGISTRY_NAME", "churn-model")
PRIMARY_METRIC = os.getenv("PRIMARY_METRIC", "roc_auc")
MIN_ACCEPTABLE_METRIC = float(os.getenv("MIN_ACCEPTABLE_METRIC", "0.60"))

RF_PARAM_GRID = json.loads(os.getenv("RF_PARAM_GRID", json.dumps(RF_PARAM_GRID)))
MLP_PARAM_GRID = json.loads(os.getenv("MLP_PARAM_GRID", json.dumps(MLP_PARAM_GRID)))
MLP_PARAM_GRID["classifier__hidden_layer_sizes"] = [
    tuple(layers) for layers in MLP_PARAM_GRID["classifier__hidden_layer_sizes"]
]
