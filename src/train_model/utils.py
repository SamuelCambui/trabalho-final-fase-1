"""Funções utilitárias para persistência e métricas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.train_model.config import MODELS_DIR


def ensure_models_dir() -> Path:
    """
    Garante que o diretório de modelos exista.

    Returns:
        Caminho absoluto do diretório ``models/``.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    return MODELS_DIR


def save_model(model: BaseEstimator, path: Path) -> Path:
    """
    Serializa um modelo treinado em disco.

    Args:
        model: Estimador ou pipeline já ajustado.
        path: Caminho do arquivo ``.joblib``.

    Returns:
        Caminho absoluto do arquivo salvo.
    """
    ensure_models_dir()
    joblib.dump(model, path)
    return path


def load_model(path: Path) -> BaseEstimator:
    """
    Carrega um modelo previamente serializado.

    Args:
        path: Caminho do arquivo ``.joblib``.

    Returns:
        Modelo ou pipeline carregado.
    """
    return joblib.load(path)


def find_dataset_csv(data_dir: Path) -> Path:
    """
    Localiza o primeiro arquivo CSV disponível no diretório de dados.

    Args:
        data_dir: Diretório onde o dataset bruto foi baixado.

    Raises:
        FileNotFoundError: Se nenhum CSV for encontrado.

    Returns:
        Caminho do arquivo CSV encontrado.
    """
    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"Nenhum CSV encontrado em {data_dir}. "
            "Execute: python scripts/setup.py"
        )
    return csv_files[0]


def compute_classification_metrics(
    y_true: pd.Series,
    y_pred,
    y_proba,
) -> dict[str, Any]:
    """
    Calcula métricas de classificação para o conjunto de teste.

    Args:
        y_true: Rótulos reais.
        y_pred: Predições discretas.
        y_proba: Probabilidades da classe positiva (churn).

    Returns:
        Dicionário com accuracy, precision, recall, f1 e roc_auc.
    """
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_proba),
    }


def print_evaluation_report(
    model_name: str,
    metrics: dict[str, Any],
    y_true: pd.Series,
    y_pred,
) -> None:
    """
    Exibe métricas e matriz de confusão no console.

    Args:
        model_name: Nome do modelo avaliado.
        metrics: Métricas retornadas por ``compute_classification_metrics``.
        y_true: Rótulos reais.
        y_pred: Predições discretas.
    """
    print(f"\n{'=' * 60}")
    print(f"Avaliação no teste: {model_name}")
    print(f"{'=' * 60}")
    for metric_name, value in metrics.items():
        print(f"{metric_name.upper():>10}: {value:.4f}")

    print("\nMatriz de confusão:")
    print(confusion_matrix(y_true, y_pred))

    print("\nRelatório de classificação:")
    print(classification_report(y_true, y_pred, zero_division=0))
