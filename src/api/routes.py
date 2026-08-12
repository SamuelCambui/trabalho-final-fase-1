from pathlib import Path

import joblib
import pandas as pd

from fastapi import APIRouter, HTTPException

from src.api.schemas import (
    CustomerRequest,
    PredictionResponse,
)


router = APIRouter()


MODEL_PATH = (
    Path(__file__).resolve()
    .parents[2]
    / "models"
    / "model.joblib"
)


try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    model = None
    model_error = str(exc)


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(customer: CustomerRequest):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail=f"Modelo não carregado: {model_error}",
        )

    try:

        data = pd.DataFrame(
            [customer.model_dump()]
        )

        probability = float(
            model.predict_proba(data)[0][1]
        )

        prediction = (
            "Yes"
            if probability >= 0.5
            else "No"
        )

        return PredictionResponse(
            prediction=prediction,
            probability=round(
                probability,
                4,
            ),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=f"Erro durante a predição: {str(exc)}",
        )