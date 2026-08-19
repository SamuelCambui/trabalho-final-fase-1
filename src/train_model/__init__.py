"""Módulo de treinamento e comparação de modelos de churn."""

from src.train_model.comparison import compare_models, evaluate_on_test
from src.train_model.preprocessing import (
    build_preprocessor,
    clean_data,
    load_data,
    prepare_features_target,
    split_data,
)
from src.train_model.train_mlp import train_mlp
from src.train_model.train_rf import train_rf

__all__ = [
    "build_preprocessor",
    "clean_data",
    "compare_models",
    "evaluate_on_test",
    "load_data",
    "prepare_features_target",
    "split_data",
    "train_mlp",
    "train_rf",
]
