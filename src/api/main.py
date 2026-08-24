from fastapi import FastAPI

from src.api.routes import router


app = FastAPI(
    title="Customer Churn Prediction API",
    description="API para previsão de churn de clientes.",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }