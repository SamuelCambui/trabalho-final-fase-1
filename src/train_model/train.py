"""
Script principal para treinar RF e MLP e comparar os modelos.

Uso:
    python -m src.modelo.train
    python -m src.modelo.train --sem-otimizacao
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.train_model.comparison import compare_models, evaluate_on_test
from src.train_model.config import BEST_MODEL_PATH, DATA_DIR
from src.train_model.preprocessing import (
    clean_data,
    load_data,
    prepare_features_target,
    split_data,
)
from src.train_model.train_mlp import train_mlp
from src.train_model.train_rf import train_rf
from src.train_model.utils import find_dataset_csv, save_model


def parse_args() -> argparse.Namespace:
    """
    Define e interpreta argumentos da linha de comando.

    Returns:
        Namespace com flags de execução do treinamento.
    """
    parser = argparse.ArgumentParser(
        description="Treina Random Forest e MLP para predição de churn.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="Caminho do CSV. Padrão: primeiro CSV em data/raw/",
    )
    parser.add_argument(
        "--sem-otimizacao",
        action="store_true",
        help="Desativa GridSearchCV (treino mais rápido).",
    )
    return parser.parse_args()


def main() -> None:
    """Executa o fluxo completo de treinamento e comparação."""
    args = parse_args()
    otimizar = not args.sem_otimizacao

    dataset_path = args.dataset or find_dataset_csv(DATA_DIR)
    print(f"Dataset: {dataset_path}")

    df = clean_data(load_data(dataset_path))
    x, y = prepare_features_target(df)
    x_train, x_test, y_train, y_test = split_data(x, y)

    print(f"Amostras de treino: {len(x_train)} | teste: {len(x_test)}")
    print(f"Distribuição de churn (treino):\n{y_train.value_counts(normalize=True)}")

    rf_model = train_rf(x_train, y_train, otimizar=otimizar)
    mlp_model = train_mlp(x_train, y_train, otimizar=otimizar)

    resultados_cv = compare_models(
        {"Random Forest": rf_model, "MLP": mlp_model},
        x_train,
        y_train,
    )
    print("\nComparação (validação cruzada):")
    print(resultados_cv.to_string(index=False))

    melhor_nome = resultados_cv.iloc[0]["Modelo"]
    modelos = {"Random Forest": rf_model, "MLP": mlp_model}
    melhor_modelo = modelos[melhor_nome]

    print(f"\nMelhor modelo (CV): {melhor_nome}")
    caminho_melhor = save_model(melhor_modelo, BEST_MODEL_PATH)
    print(f"Melhor modelo salvo para API em: {caminho_melhor}")

    for nome, modelo in modelos.items():
        evaluate_on_test(modelo, x_test, y_test, nome)


if __name__ == "__main__":
    main()
