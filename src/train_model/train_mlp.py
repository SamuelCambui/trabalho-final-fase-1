"""Treinamento do modelo MLP (Multi-Layer Perceptron)."""

from __future__ import annotations

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline

from src.train_model.config import (
    CV_FOLDS,
    MLP_MODEL_PATH,
    MLP_PARAM_GRID,
    RANDOM_STATE,
    SCORING,
)
from src.train_model.preprocessing import build_preprocessor
from src.train_model.utils import save_model


def _build_mlp_pipeline(x_train: pd.DataFrame) -> Pipeline:
    """
    Monta o pipeline completo de pré-processamento + MLP.

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
                MLPClassifier(
                    hidden_layer_sizes=(64, 32),
                    max_iter=500,
                    early_stopping=True,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def train_mlp(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    otimizar: bool = True,
    salvar: bool = True,
) -> BaseEstimator:
    """
    Treina uma rede MLP com ou sem busca de hiperparâmetros.

    Args:
        x_train: Features de treino.
        y_train: Target de treino.
        otimizar: Se ``True``, executa grid search com validação cruzada.
        salvar: Se ``True``, persiste o modelo em ``models/mlp_model.joblib``.

    Returns:
        Pipeline treinado (melhor estimador quando ``otimizar=True``).
    """
    pipeline = _build_mlp_pipeline(x_train)

    if otimizar:
        grid = GridSearchCV(
            estimator=pipeline,
            param_grid=MLP_PARAM_GRID,
            cv=CV_FOLDS,
            scoring=SCORING,
            n_jobs=-1,
        )
        grid.fit(x_train, y_train)
        modelo = grid.best_estimator_
        print(f"Melhores parâmetros (MLP): {grid.best_params_}")
        print(f"Melhor {SCORING} (CV): {grid.best_score_:.4f}")
    else:
        modelo = pipeline
        modelo.fit(x_train, y_train)
        print("MLP treinado sem otimização de hiperparâmetros.")

    if salvar:
        caminho = save_model(modelo, MLP_MODEL_PATH)
        print(f"Modelo MLP salvo em: {caminho}")

    return modelo
