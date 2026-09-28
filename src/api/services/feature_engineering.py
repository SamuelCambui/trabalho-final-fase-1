"""Feature engineering alinhado ao notebook de modelagem (champion LR)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Mediana de TotalCharges no treino (EDA, random_state=42, test_size=0.2).
TOTAL_CHARGES_TRAIN_MEDIAN = 1398.12
EPS = 1

ADDON_SERVICE_COLS = (
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
)

# Ordem exata esperada por notebooks/models/champion_model.joblib
CHAMPION_FEATURE_COLUMNS = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "charges_ratio",
    "tenure_years",
    "is_new_customer",
    "charges_per_service",
    "is_month_to_month",
    "is_electronic_check",
    "has_fiber_optic",
    "has_internet",
    "new_and_monthly",
    "fiber_and_echeck",
    "InternetService_Fiber optic",
    "Contract_Two year",
    "PaperlessBilling_Yes",
    "PaymentMethod_Electronic check",
    "tenure_group_49-72m",
]


def _as_int_flag(condition: bool) -> int:
    return int(bool(condition))


def transform_customer_features(customer_data: dict[str, Any]) -> pd.DataFrame:
    """
    Converte o payload bruto Telco nas 18 features do modelo campeão.

    O pipeline serializado já inclui ``StandardScaler``; esta função devolve
    as features **sem** escala adicional.
    """
    tenure = int(customer_data["tenure"])
    monthly_charges = float(customer_data["MonthlyCharges"])
    total_charges = customer_data.get("TotalCharges")

    if total_charges is None or (
        isinstance(total_charges, float) and pd.isna(total_charges)
    ):
        total_charges = TOTAL_CHARGES_TRAIN_MEDIAN
    else:
        total_charges = float(total_charges)

    contract = str(customer_data["Contract"])
    payment_method = str(customer_data["PaymentMethod"])
    internet_service = str(customer_data["InternetService"])
    paperless_billing = str(customer_data["PaperlessBilling"])

    avg_monthly_spend = total_charges / (tenure + EPS)
    charges_ratio = monthly_charges / (avg_monthly_spend + EPS)
    tenure_years = tenure // 12
    is_new_customer = _as_int_flag(tenure <= 6)

    num_addon_services = sum(
        1 for col in ADDON_SERVICE_COLS if str(customer_data.get(col, "No")) == "Yes"
    )
    charges_per_service = monthly_charges / (num_addon_services + EPS)

    is_month_to_month = _as_int_flag(contract == "Month-to-month")
    is_electronic_check = _as_int_flag(payment_method == "Electronic check")
    has_fiber_optic = _as_int_flag(internet_service == "Fiber optic")
    has_internet = _as_int_flag(internet_service != "No")
    new_and_monthly = is_new_customer * is_month_to_month
    fiber_and_echeck = has_fiber_optic * is_electronic_check

    features = {
        "tenure": tenure,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
        "charges_ratio": charges_ratio,
        "tenure_years": tenure_years,
        "is_new_customer": is_new_customer,
        "charges_per_service": charges_per_service,
        "is_month_to_month": is_month_to_month,
        "is_electronic_check": is_electronic_check,
        "has_fiber_optic": has_fiber_optic,
        "has_internet": has_internet,
        "new_and_monthly": new_and_monthly,
        "fiber_and_echeck": fiber_and_echeck,
        "InternetService_Fiber optic": has_fiber_optic,
        "Contract_Two year": _as_int_flag(contract == "Two year"),
        "PaperlessBilling_Yes": _as_int_flag(paperless_billing == "Yes"),
        "PaymentMethod_Electronic check": is_electronic_check,
        "tenure_group_49-72m": _as_int_flag(48 < tenure <= 72),
    }

    return pd.DataFrame([features], columns=CHAMPION_FEATURE_COLUMNS)


class FeatureEngineeringTransformer(BaseEstimator, TransformerMixin):
    """Wrapper sklearn-compatível em torno de ``transform_customer_features``.

    Segue a mesma convenção fit/transform que qualquer outro passo do
    scikit-learn (duck typing: basta implementar ``fit``/``transform`` para
    ser tratado como parte do ecossistema, sem herança complexa — Aula 7).
    Isso permite compor a engenharia de features com o modelo treinado em
    um único ``sklearn.pipeline.Pipeline``, com uma única interface
    ``predict``/``predict_proba`` de ponta a ponta, em vez de chamar a
    função manualmente antes de invocar o modelo.

    Não possui estado a ajustar (a transformação é puramente derivada do
    payload de entrada), então ``fit`` apenas retorna ``self``.
    """

    def fit(
        self, X: dict[str, Any], y: Any = None
    ) -> "FeatureEngineeringTransformer":
        """Não-op: a transformação não depende de dados de treino."""
        return self

    def transform(self, X: dict[str, Any]) -> pd.DataFrame:
        """Aplica ``transform_customer_features`` ao payload bruto do cliente."""
        return transform_customer_features(X)
