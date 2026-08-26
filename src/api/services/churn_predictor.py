"""Serviço responsável por carregar o modelo e executar predições."""

from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from src.api.services.feature_engineering import transform_customer_features


class ChurnPredictorService:
    """Encapsula o pipeline campeão e a lógica de inferência."""

    def __init__(
        self,
        model_path: Path,
        threshold: float = 0.5,
        probability_decimals: int = 4,
    ) -> None:
        self.model_path = model_path
        self.threshold = threshold
        self.probability_decimals = probability_decimals
        self._model: BaseEstimator | None = None
        self._load_error: str | None = None

    @property
    def is_loaded(self) -> bool:
        """Indica se o modelo foi carregado com sucesso."""
        return self._model is not None

    @property
    def load_error(self) -> str | None:
        """Retorna a mensagem de erro do carregamento, se houver."""
        return self._load_error

    def load(self) -> None:
        """Carrega o pipeline treinado a partir do disco."""
        try:
            self._model = joblib.load(self.model_path)
            self._load_error = None
        except Exception as exc:
            self._model = None
            self._load_error = str(exc)

    def get_model_type(self) -> str:
        """Retorna o tipo do classificador presente no pipeline."""
        if not self.is_loaded or self._model is None:
            return "unknown"

        if isinstance(self._model, Pipeline):
            for step_name in ("model", "classifier"):
                estimator = self._model.named_steps.get(step_name)
                if estimator is not None:
                    return type(estimator).__name__

        return type(self._model).__name__

    def predict(self, customer_data: dict) -> tuple[str, float]:
        """
        Gera predição de churn para um único cliente.

        Aplica a engenharia de features do notebook e usa o pipeline
        ``StandardScaler`` + ``LogisticRegression``.

        Args:
            customer_data: Dicionário com as features brutas do cliente Telco.

        Raises:
            RuntimeError: Se o modelo não estiver carregado.
            ValueError: Se a inferência falhar por inconsistência de dados.

        Returns:
            Tupla ``(predição, probabilidade)``.
        """
        if not self.is_loaded or self._model is None:
            raise RuntimeError(
                f"Modelo não carregado: {self._load_error or 'arquivo ausente'}"
            )

        try:
            features = transform_customer_features(customer_data)
            probability = float(self._model.predict_proba(features)[0][1])
        except Exception as exc:
            raise ValueError(f"Erro durante a predição: {exc}") from exc

        prediction = "Yes" if probability >= self.threshold else "No"
        rounded_probability = round(probability, self.probability_decimals)
        return prediction, rounded_probability
