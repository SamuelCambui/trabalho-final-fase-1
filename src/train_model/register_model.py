"""Registra a versao mais recente do modelo no MLflow Model Registry.

Promove o alias ``Production`` para ela SOMENTE se a metrica principal
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

import mlflow
from mlflow import MlflowClient
from mlflow.entities.model_registry import ModelVersion

from src.train_model.config import MODEL_REGISTRY_NAME, PRIMARY_METRIC
from src.train_model.mlflow_utils import resolve_tracking_paths


def resolve_metadata_path(metadata_path: str | None, tracking_dir: str | None) -> Path:
    """Decide de onde ler o ``latest_run.json``.

    Args:
        metadata_path: Caminho explicito, se o chamador souber onde o
            arquivo esta (ex.: passado via ``--metadata-path``).
        tracking_dir: Pasta de tracking do MLflow, usada como local
            padrao quando ``metadata_path`` nao e informado.

    Returns:
        Caminho do arquivo de metadata a ser lido (ainda nao
        verificado quanto a existencia).

    Raises:
        ValueError: Se nenhum dos dois caminhos puder ser determinado.
    """
    if metadata_path:
        return Path(metadata_path)
    if not tracking_dir:
        raise ValueError(
            "Nao foi possivel determinar a pasta de tracking do MLflow. "
            "Defina MLFLOW_TRACKING_URI ou MLFLOW_TRACKING_FOLDER."
        )
    return Path(tracking_dir) / "latest_run.json"


def read_run_metadata(metadata_file: Path) -> dict:
    """Le e valida o ``latest_run.json`` gerado pelo ``train.py``.

    Args:
        metadata_file: Caminho do arquivo JSON a ler.

    Returns:
        O conteudo do arquivo, com ao menos ``run_id`` e ``model_uri``.

    Raises:
        ValueError: Se o arquivo nao tiver run_id ou model_uri.
    """
    print(f"Carregando metadata: {metadata_file}")
    with open(metadata_file, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    if not data.get("run_id") or not data.get("model_uri"):
        raise ValueError("Metadata incompleta: run_id ou model_uri ausentes.")
    return data


def set_production_alias(client: MlflowClient, model_name: str, version: str) -> None:
    """Atualiza o alias Production e propaga falhas de infraestrutura."""
    client.set_registered_model_alias(model_name, "Production", version)
    print(f"  OK: alias 'Production' atualizado para versao {version}.")


def find_best_previous_version(
    client: MlflowClient,
    model_name: str,
    current_version: str,
) -> tuple[str | None, float | None, bool]:
    """Retorna melhor versão, métrica e existência de versões anteriores."""
    todas_versoes = client.search_model_versions(f"name='{model_name}'")
    anteriores = [v for v in todas_versoes if str(v.version) != str(current_version)]

    melhor_versao: str | None = None
    melhor_metrica: float | None = None
    for versao in anteriores:
        if not versao.run_id:
            continue
        run = client.get_run(versao.run_id)
        metrica = run.data.metrics.get(PRIMARY_METRIC)
        if metrica is not None and (
            melhor_metrica is None or metrica > melhor_metrica
        ):
            melhor_metrica = float(metrica)
            melhor_versao = str(versao.version)

    return melhor_versao, melhor_metrica, bool(anteriores)


def should_promote(
    current_metric: float | None,
    previous_metric: float | None,
    is_first_version: bool,
) -> bool:
    """Permite primeira versão válida ou melhora estrita sobre a anterior."""
    if current_metric is None:
        return False
    if is_first_version:
        return True
    if previous_metric is None:
        return False
    return current_metric > previous_metric


def decide_promotion(
    client: MlflowClient,
    model_name: str,
    new_version: ModelVersion,
    metrica_atual: float | None,
) -> None:
    """Decide a promoção e atualiza Production somente quando permitido."""
    versao_anterior, metrica_anterior, has_previous = find_best_previous_version(
        client, model_name, str(new_version.version)
    )
    is_first_version = not has_previous
    if not should_promote(metrica_atual, metrica_anterior, is_first_version):
        print("  Modelo nao promovido: metrica ausente ou sem melhora comprovada.")
        return

    if is_first_version:
        print("  Primeira versao valida registrada. Promovendo para Production.")
    else:
        print(
            f"  Melhor {PRIMARY_METRIC} anterior: {metrica_anterior:.4f} "
            f"(versao {versao_anterior})"
        )
    set_production_alias(client, model_name, str(new_version.version))
    print(f"  Versao {new_version.version} promovida para Production.")

def register_and_promote(model_name: str, metadata_path: str | None) -> None:
    """Registra a ultima run treinada e promove-a se for a melhor.

    Orquestra o fluxo completo: resolve onde esta o metadata, le e
    valida o conteudo, registra a versao no MLflow Model Registry e
    decide se ela deve virar a versao ``Production``.

    Args:
        model_name: Nome do modelo no Model Registry.
        metadata_path: Caminho explicito do ``latest_run.json``, ou
            ``None`` para usar a pasta de tracking padrao.
    """
    tracking_uri, tracking_dir = resolve_tracking_paths()
    mlflow.set_tracking_uri(tracking_uri)
    print(f"MLflow tracking URI: {tracking_uri}")

    metadata_file = resolve_metadata_path(metadata_path, tracking_dir)
    data = read_run_metadata(metadata_file)

    client = MlflowClient()
    print(f"Registrando nova versao no Model Registry ({model_name})...")
    new_version = mlflow.register_model(model_uri=data["model_uri"], name=model_name)

    decide_promotion(client, model_name, new_version, data.get(PRIMARY_METRIC))


def main() -> None:
    """Ponto de entrada de linha de comando do script de registro."""
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
