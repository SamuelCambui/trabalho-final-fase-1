"""Comparação de modelos via validação cruzada e conjunto de teste."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.model_selection import cross_validate

from src.train_model.config import COMPARISON_REPORT_PATH, CV_FOLDS, SCORING

CV_SCORE_LABEL = "ROC-AUC Médio"
from src.train_model.utils import (
    compute_classification_metrics,
    ensure_models_dir,
    print_evaluation_report,
)


def cross_validate_model(
    pipeline: BaseEstimator,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    model_name: str,
) -> dict[str, float]:
    """
    Executa validação cruzada e resume média e desvio padrão da métrica.

    Args:
        pipeline: Pipeline treinado ou não treinado.
        x_train: Features de treino.
        y_train: Target de treino.
        model_name: Nome exibido nos relatórios.

    Returns:
        Dicionário com nome, média e desvio padrão do score de CV.
    """
    scores = cross_validate(
        pipeline,
        x_train,
        y_train,
        cv=CV_FOLDS,
        scoring=SCORING,
        return_train_score=False,
    )
    test_scores = scores["test_score"]

    return {
        "Modelo": model_name,
        CV_SCORE_LABEL: test_scores.mean(),
        "Desvio Padrão": test_scores.std(),
    }


def compare_models(
    modelos: dict[str, BaseEstimator],
    x_train: pd.DataFrame,
    y_train: pd.Series,
    salvar_relatorio: bool = True,
) -> pd.DataFrame:
    """
    Compara modelos com validação cruzada no conjunto de treino.

    Args:
        modelos: Dicionário ``{nome: pipeline}`` a ser comparado.
        x_train: Features de treino.
        y_train: Target de treino.
        salvar_relatorio: Se ``True``, exporta CSV em ``models/``.

    Returns:
        DataFrame ordenado pelo melhor score médio.
    """
    resultados = [
        cross_validate_model(pipeline, x_train, y_train, nome)
        for nome, pipeline in modelos.items()
    ]
    df_resultados = pd.DataFrame(resultados).sort_values(
        by=CV_SCORE_LABEL,
        ascending=False,
    )

    if salvar_relatorio:
        ensure_models_dir()
        df_resultados.to_csv(COMPARISON_REPORT_PATH, index=False)
        print(f"Relatório de comparação salvo em: {COMPARISON_REPORT_PATH}")

    return df_resultados.reset_index(drop=True)


def evaluate_on_test(
    pipeline: BaseEstimator,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
    exibir_relatorio: bool = True,
) -> dict[str, Any]:
    """
    Avalia um pipeline no conjunto de teste hold-out.

    Args:
        pipeline: Modelo já treinado.
        x_test: Features de teste.
        y_test: Target de teste.
        model_name: Nome exibido nos relatórios.
        exibir_relatorio: Se ``True``, imprime métricas no console.

    Returns:
        Dicionário com métricas e predições.
    """
    y_pred = pipeline.predict(x_test)
    y_proba = pipeline.predict_proba(x_test)[:, 1]
    metrics = compute_classification_metrics(y_test, y_pred, y_proba)

    if exibir_relatorio:
        print_evaluation_report(model_name, metrics, y_test, y_pred)

    return {
        "model_name": model_name,
        "metrics": metrics,
        "y_pred": y_pred,
        "y_proba": y_proba,
    }
