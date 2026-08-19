"""Treinamento do modelo Random Forest."""

from __future__ import annotations

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from src.train_model.config import (
    CV_FOLDS,
    RF_MODEL_PATH,
    RF_PARAM_GRID,
    RANDOM_STATE,
    SCORING,
)
from src.train_model.preprocessing import build_preprocessor
from src.train_model.utils import save_model


def _build_rf_pipeline(x_train: pd.DataFrame) -> Pipeline:
    """
    Monta o pipeline completo de pré-processamento + Random Forest.

    Args:
        x_train: Features de treino para configurar o pré-processador.

    Returns:
        Pipeline pronto para ``fit``.
    """
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(x_train)),
            (
                "classifier",
                RandomForestClassifier(
                    random_state=RANDOM_STATE,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
            ),
        ]
    )


def train_rf(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    otimizar: bool = True,
    salvar: bool = True,
) -> BaseEstimator:
    """
    Treina um Random Forest com ou sem busca de hiperparâmetros.

    A otimização usa ``GridSearchCV`` sobre o pipeline completo, garantindo
    que pré-processamento e modelo sejam ajustados sem vazamento de dados.

    Args:
        x_train: Features de treino.
        y_train: Target de treino.
        otimizar: Se ``True``, executa grid search com validação cruzada.
        salvar: Se ``True``, persiste o modelo em ``models/rf_model.joblib``.

    Returns:
        Pipeline treinado (melhor estimador quando ``otimizar=True``).
    """
    pipeline = _build_rf_pipeline(x_train)

    if otimizar:
        grid = GridSearchCV(
            estimator=pipeline,
            param_grid=RF_PARAM_GRID,
            cv=CV_FOLDS,
            scoring=SCORING,
            n_jobs=-1,
        )
        grid.fit(x_train, y_train)
        modelo = grid.best_estimator_
        print(f"Melhores parâmetros (RF): {grid.best_params_}")
        print(f"Melhor {SCORING} (CV): {grid.best_score_:.4f}")
    else:
        modelo = pipeline
        modelo.fit(x_train, y_train)
        print("Random Forest treinado sem otimização de hiperparâmetros.")

    if salvar:
        caminho = save_model(modelo, RF_MODEL_PATH)
        print(f"Modelo RF salvo em: {caminho}")

    return modelo
