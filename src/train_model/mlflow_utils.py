"""Utilitarios compartilhados para configuracao do MLflow no pipeline de CI/CD.

Segue o mesmo padrao usado no material da Aula 06: execucoes locais usam uma
pasta ignorada pelo git (mlruns_local/), enquanto o GitHub Actions usa uma
pasta versionada (mlruns_ci_snapshot/) para manter o historico de runs e
permitir comparar a metrica atual com a melhor versao anterior sem precisar
de um servidor MLflow remoto.
"""

from __future__ import annotations

import os
from pathlib import Path

from src.train_model.config import PROJECT_ROOT

# A partir do MLflow 3.x, o backend de arquivo local ("file://...") entra
# em modo de manutencao por padrao e levanta excecao ao ser usado, a nao
# ser que esta variavel seja definida. Mantemos o backend de arquivo de
# proposito (ver docstring do modulo: compara runs locais sem precisar de
# um servidor MLflow remoto), entao fazemos o opt-out aqui, de forma
# centralizada, em vez de exigir que cada ambiente (local, CI) configure
# a variavel manualmente.
os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")


def resolve_tracking_paths() -> tuple[str, str | None]:
    """Retorna (tracking_uri, tracking_dir) usando env vars ou defaults.

    Prioridade:
        1. MLFLOW_TRACKING_URI (ex.: servidor remoto configurado via secret)
        2. MLFLOW_TRACKING_FOLDER (nome de pasta local, relativo a raiz do projeto)
        3. Default: "mlruns_ci_snapshot" quando rodando em CI (env CI=true),
           "mlruns_local" quando rodando localmente.

    Returns:
        Tupla ``(tracking_uri, tracking_dir)``. ``tracking_dir`` é
        ``None`` quando ``MLFLOW_TRACKING_URI`` aponta para um destino
        que não é uma pasta local (ex.: um servidor remoto).
    """
    tracking_uri_env = os.environ.get("MLFLOW_TRACKING_URI")
    tracking_dir: str | None = None

    if tracking_uri_env:
        tracking_uri = tracking_uri_env
        if tracking_uri.startswith("file://"):
            tracking_dir = tracking_uri[len("file://") :]
    else:
        tracking_folder = os.environ.get("MLFLOW_TRACKING_FOLDER")
        if not tracking_folder:
            tracking_folder = (
                "mlruns_ci_snapshot" if os.environ.get("CI") else "mlruns_local"
            )

        tracking_path = Path(tracking_folder)
        if not tracking_path.is_absolute():
            tracking_path = PROJECT_ROOT / tracking_path

        tracking_path.mkdir(parents=True, exist_ok=True)
        tracking_dir = str(tracking_path)
        tracking_uri = f"file://{tracking_dir}"

    return tracking_uri, tracking_dir
