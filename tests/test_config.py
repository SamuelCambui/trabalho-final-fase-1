"""Environment overrides work independently of the current directory."""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_configuration_overrides_and_relative_paths(tmp_path):
    env = dict(
        os.environ,
        PYTHONPATH=str(PROJECT_ROOT),
        MODEL_PATH="models/custom.joblib",
        DATA_DIR="data/custom",
        RANDOM_STATE="7",
        TEST_SIZE="0.2",
        PREDICTION_THRESHOLD="0.7",
        API_ADMIN_PASSWORD="custom-password",
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from src.api.config import ("
                "MODEL_PATH, PREDICTION_THRESHOLD, USERS_DB); "
                "from src.train_model.config import DATA_DIR, RANDOM_STATE, TEST_SIZE; "
                "assert str(MODEL_PATH) == "
                f"{str(PROJECT_ROOT / 'models/custom.joblib')!r}; "
                f"assert str(DATA_DIR) == {str(PROJECT_ROOT / 'data/custom')!r}; "
                "assert RANDOM_STATE == 7 and TEST_SIZE == 0.2; "
                "assert PREDICTION_THRESHOLD == 0.7; "
                "assert USERS_DB['admin']['password'] == 'custom-password'"
            ),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_placeholder_secret_is_rejected(tmp_path):
    env = dict(
        os.environ,
        PYTHONPATH=str(PROJECT_ROOT),
        SECRET_KEY="altere-esta-chave-em-producao",
    )
    result = subprocess.run(
        [sys.executable, "-c", "import src.api.config"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Configure SECRET_KEY" in result.stderr
