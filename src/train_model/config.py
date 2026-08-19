"""Constantes e hiperparâmetros do pipeline de treinamento."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
MODELS_DIR = PROJECT_ROOT / "models"

TARGET_COLUMN = "Churn"
ID_COLUMN = "customerID"
RANDOM_STATE = 42
TEST_SIZE = 0.3
CV_FOLDS = 5
SCORING = "roc_auc"

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
