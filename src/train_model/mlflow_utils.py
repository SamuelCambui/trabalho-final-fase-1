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
from typing import Optional, Tuple

from src.train_model.config import PROJECT_ROOT


def resolve_tracking_paths() -> Tuple[str, Optional[str]]:
    """Retorna (tracking_uri, tracking_dir) usando env vars ou defaults.

    Prioridade:
        1. MLFLOW_TRACKING_URI (ex.: servidor remoto configurado via secret)
        2. MLFLOW_TRACKING_FOLDER (nome de pasta local, relativo a raiz do projeto)
        3. Default: "mlruns_ci_snapshot" quando rodando em CI (env CI=true),
           "mlruns_local" quando rodando localmente.
    """
    tracking_uri_env = os.environ.get("MLFLOW_TRACKING_URI")
    tracking_dir: Optional[str] = None

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