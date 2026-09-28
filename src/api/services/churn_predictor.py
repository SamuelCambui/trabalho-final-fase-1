"""Serviço responsável por carregar o modelo e executar predições."""

from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from src.api.services.feature_engineering import FeatureEngineeringTransformer


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
        # Pipeline de inferência: compõe a engenharia de features (não
        # treinável, ver FeatureEngineeringTransformer) com o modelo
        # campeão já treinado (StandardScaler + LogisticRegression) em um
        # único objeto, com uma interface fit/predict uniforme (Aula 7).
        # Construído em load(), quando o modelo já está disponível.
        self._inference_pipeline: Pipeline | None = None

    @property
    def is_loaded(self) -> bool:
        """Indica se o modelo foi carregado com sucesso."""
        return self._model is not None

    @property
    def load_error(self) -> str | None:
        """Retorna a mensagem de erro do carregamento, se houver."""
        return self._load_error

    def load(self) -> None:
        """Carrega o pipeline treinado a partir do disco.

        Também compõe o pipeline de inferência (features + modelo) em um
        único objeto, para que ``predict`` faça uma única chamada
        ``predict_proba`` de ponta a ponta.
        """
        try:
            self._model = joblib.load(self.model_path)
            self._inference_pipeline = Pipeline(
                [
                    ("feature_engineering", FeatureEngineeringTransformer()),
                    ("model", self._model),
                ]
            )
            self._load_error = None
        except Exception as exc:
            self._model = None
            self._inference_pipeline = None
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

        Usa o pipeline de inferência único (engenharia de features ->
        ``StandardScaler`` -> ``LogisticRegression``), composto em
        ``load()``. O caller não precisa saber que a transformação e o
        modelo são objetos separados por baixo do capô.

        Args:
            customer_data: Dicionário com as features brutas do cliente Telco.

        Raises:
            RuntimeError: Se o modelo não estiver carregado.
            ValueError: Se a inferência falhar por inconsistência de dados.

        Returns:
            Tupla ``(predição, probabilidade)``.
        """
        if not self.is_loaded or self._inference_pipeline is None:
            raise RuntimeError(
                f"Modelo não carregado: {self._load_error or 'arquivo ausente'}"
            )

        try:
            probability = float(
                self._inference_pipeline.predict_proba(customer_data)[0][1]
            )
        except Exception as exc:
            raise ValueError(f"Erro durante a predição: {exc}") from exc

        prediction = "Yes" if probability >= self.threshold else "No"
        rounded_probability = round(probability, self.probability_decimals)
        return prediction, rounded_probability
