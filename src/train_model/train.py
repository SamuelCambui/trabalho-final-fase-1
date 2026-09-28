"""
Script principal para treinar RF e MLP e comparar os modelos.

Uso:
    python -m src.modelo.train
    python -m src.modelo.train --sem-otimizacao
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import mlflow
import mlflow.sklearn

from src.train_model.comparison import compare_models, evaluate_on_test
from src.train_model.config import (
    BEST_MODEL_PATH,
    DATA_DIR,
    MIN_ACCEPTABLE_METRIC,
    MLFLOW_EXPERIMENT_NAME,
    PRIMARY_METRIC,
)
from src.train_model.mlflow_utils import resolve_tracking_paths
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

    resultados_teste: dict[str, dict] = {}
    for nome, modelo in modelos.items():
        resultados_teste[nome] = evaluate_on_test(modelo, x_test, y_test, nome)

    log_mlflow(
        melhor_nome=melhor_nome,
        melhor_modelo=melhor_modelo,
        resultados_cv=resultados_cv,
        resultados_teste=resultados_teste,
        x_train=x_train,
    )

    metrica_principal = resultados_teste[melhor_nome]["metrics"][PRIMARY_METRIC]
    if metrica_principal < MIN_ACCEPTABLE_METRIC:
        print(
            f"\n[ERRO] {PRIMARY_METRIC}={metrica_principal:.4f} abaixo do minimo "
            f"aceitavel ({MIN_ACCEPTABLE_METRIC}). Verifique dados/hiperparametros."
        )
        sys.exit(1)


def log_mlflow(
    *,
    melhor_nome: str,
    melhor_modelo,
    resultados_cv,
    resultados_teste: dict[str, dict],
    x_train,
) -> None:
    """Loga parametros, metricas e o modelo vencedor no MLflow.

    Tambem grava um arquivo ``latest_run.json`` na pasta de tracking, usado
    pelo ``register_model.py`` para registrar/promover a versao no Model
    Registry (ponte entre o job de treino e o job de registro no CI).
    """
    tracking_uri, tracking_dir = resolve_tracking_paths()
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    print(f"\nMLflow tracking URI: {tracking_uri}")

    run_name = melhor_nome.lower().replace(" ", "_")
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_param("modelo_selecionado", melhor_nome)

        for _, linha in resultados_cv.iterrows():
            nome_modelo = linha["Modelo"].lower().replace(" ", "_")
            mlflow.log_metric(f"cv_{nome_modelo}_roc_auc", linha["ROC-AUC Médio"])

        for nome_modelo, resultado in resultados_teste.items():
            prefixo = nome_modelo.lower().replace(" ", "_")
            for metrica, valor in resultado["metrics"].items():
                mlflow.log_metric(f"{prefixo}_test_{metrica}", valor)

        metricas_vencedor = resultados_teste[melhor_nome]["metrics"]

        model_info = mlflow.sklearn.log_model(
            sk_model=melhor_modelo,
            name="model",
            input_example=x_train.iloc[:5],
        )

        print(f"  Run ID: {run.info.run_id}")
        print(f"  Model URI: {model_info.model_uri}")

        metadata = {
            "run_id": run.info.run_id,
            "model_uri": model_info.model_uri,
            "modelo_selecionado": melhor_nome,
            PRIMARY_METRIC: metricas_vencedor[PRIMARY_METRIC],
            "metrics": metricas_vencedor,
            "logged_at": datetime.now(timezone.utc).isoformat(),
        }

        metadata_path = (
            Path(tracking_dir) / "latest_run.json" if tracking_dir else None
        )
        if metadata_path:
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"  Metadata salva em: {metadata_path}")
            print("  -> Execute register_model.py para atualizar o Model Registry.")
        else:
            print("  [AVISO] Nao foi possivel determinar caminho para a metadata.")


if __name__ == "__main__":
    main()