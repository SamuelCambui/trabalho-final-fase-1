"""Deterministic credentials used only by the test suite."""
import os

os.environ["SECRET_KEY"] = "test-only-secret-key-do-not-use-in-production"
os.environ["API_ADMIN_USERNAME"] = "admin"
os.environ["API_ADMIN_PASSWORD"] = "admin"
os.environ["API_USER_USERNAME"] = "user"
os.environ["API_USER_PASSWORD"] = "user"

os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
