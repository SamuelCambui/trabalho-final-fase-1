"""Registra a versao mais recente do modelo no MLflow Model Registry e
promove o alias ``Production`` para ela SOMENTE se a metrica principal
(``PRIMARY_METRIC``, default roc_auc) superar a melhor versao ja registrada.

Uso:
    python -m src.train_model.register_model

Le o arquivo ``latest_run.json`` (gerado pelo ``train.py``) na pasta de
tracking do MLflow para saber qual run/model_uri registrar.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import mlflow
from mlflow import MlflowClient

from src.train_model.config import MODEL_REGISTRY_NAME, PRIMARY_METRIC
from src.train_model.mlflow_utils import resolve_tracking_paths


def load_metadata(metadata_path: Optional[str], tracking_dir: Optional[str]) -> Path:
    if metadata_path:
        return Path(metadata_path)
    if not tracking_dir:
        raise ValueError(
            "Nao foi possivel determinar a pasta de tracking do MLflow. "
            "Defina MLFLOW_TRACKING_URI ou MLFLOW_TRACKING_FOLDER."
        )
    return Path(tracking_dir) / "latest_run.json"


def register_and_promote(model_name: str, metadata_path: Optional[str]) -> None:
    tracking_uri, tracking_dir = resolve_tracking_paths()
    mlflow.set_tracking_uri(tracking_uri)
    print(f"MLflow tracking URI: {tracking_uri}")

    metadata_file = load_metadata(metadata_path, tracking_dir)
    print(f"Carregando metadata: {metadata_file}")
    with open(metadata_file, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    run_id = data.get("run_id")
    model_uri = data.get("model_uri")
    metrica_atual = data.get(PRIMARY_METRIC)

    if not run_id or not model_uri:
        raise ValueError("Metadata incompleta: run_id ou model_uri ausentes.")

    client = MlflowClient()

    print(f"Registrando nova versao no Model Registry ({model_name})...")
    model_version = mlflow.register_model(model_uri=model_uri, name=model_name)

    def set_alias(version: str) -> None:
        try:
            client.set_registered_model_alias(model_name, "Production", version)
            print(f"  OK: alias 'Production' atualizado para versao {version}.")
        except Exception as exc:  # pragma: no cover - so em falha de infra
            print(f"  AVISO: falha ao atualizar alias Production: {exc}")

    try:
        todas_versoes = client.search_model_versions(f"name='{model_name}'")
    except Exception:
        todas_versoes = []

    versoes_anteriores = [
        v for v in todas_versoes if v.version != model_version.version
    ]

    if not versoes_anteriores:
        print("  Primeira versao registrada. Promovendo para Production.")
        set_alias(model_version.version)
        return

    melhor_metrica_anterior = None
    melhor_versao_anterior = None
    for versao in versoes_anteriores:
        run_id_anterior = getattr(versao, "run_id", None)
        if not run_id_anterior:
            continue
        try:
            run_anterior = client.get_run(run_id_anterior)
            metrica_anterior = run_anterior.data.metrics.get(PRIMARY_METRIC)
            if metrica_anterior is not None and (
                melhor_metrica_anterior is None
                or metrica_anterior > melhor_metrica_anterior
            ):
                melhor_metrica_anterior = metrica_anterior
                melhor_versao_anterior = versao.version
        except Exception:
            continue

    if melhor_metrica_anterior is None or metrica_atual is None:
        print("  Nao foi possivel comparar metricas. Mantendo Production atual.")
        return

    print(
        f"  Melhor {PRIMARY_METRIC} anterior: {melhor_metrica_anterior:.4f} "
        f"(versao {melhor_versao_anterior})"
    )
    if metrica_atual > melhor_metrica_anterior:
        set_alias(model_version.version)
        print(
            f"  OK: versao {model_version.version} promovida a Production "
            f"({PRIMARY_METRIC} {metrica_atual:.4f} > {melhor_metrica_anterior:.4f})."
        )
    else:
        print(
            f"  {PRIMARY_METRIC} {metrica_atual:.4f} nao supera "
            f"{melhor_metrica_anterior:.4f}. Mantem Production existente "
            f"(versao {melhor_versao_anterior})."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Registrar e promover modelo no MLflow Model Registry"
    )
    parser.add_argument(
        "--metadata-path",
        type=str,
        default=None,
        help="Caminho explicito para o latest_run.json (opcional)",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=MODEL_REGISTRY_NAME,
        help="Nome do modelo no Model Registry",
    )
    args = parser.parse_args()
    register_and_promote(model_name=args.model_name, metadata_path=args.metadata_path)


if __name__ == "__main__":
    main()