"""Métricas customizadas do Prometheus.

Além das métricas HTTP genéricas que o `prometheus-fastapi-
instrumentator` já expõe automaticamente (contagem de requisições,
latência por rota, etc. — ver main.py), este módulo define métricas
de negócio, específicas do domínio de predição de churn.

Três tipos de métrica são usados aqui, cada um com um propósito:

    Counter   — soma eventos que só aumentam (nunca diminuem).
                Ex.: total de predições realizadas.
    Histogram — distribuição de valores; permite calcular percentis
                (p50, p95, p99) no Prometheus/Grafana depois.
                Ex.: latência de uma predição.
    Gauge     — um valor que pode subir e descer; representa um
                estado atual, não um acumulado.
                Ex.: "o modelo está carregado?" (1 ou 0).

Essas métricas ficam expostas em texto plano no endpoint /metrics
(configurado em main.py) e o Prometheus as coleta ("faz scrape")
periodicamente, conforme prometheus/prometheus.yml.
"""

from prometheus_client import Counter, Gauge, Histogram

# ============================================================
# CONTADORES (Counter)
# ============================================================

PREDICTIONS_TOTAL = Counter(
    "churn_predictions_total",
    "Total de predições de churn realizadas",
    ["classe", "user"],  # labels para filtrar no Prometheus/Grafana
)

LOGIN_ATTEMPTS = Counter(
    "login_attempts_total",
    "Total de tentativas de login",
    ["status"],  # success ou failed
)

ERRORS_TOTAL = Counter(
    "api_errors_total",
    "Total de erros da API",
    ["endpoint", "error_type"],
)

# ============================================================
# HISTOGRAMAS (Histogram)
# ============================================================

PREDICTION_LATENCY = Histogram(
    "churn_prediction_latency_seconds",
    "Latência das predições de churn, em segundos",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Latência das requisições HTTP, em segundos",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# ============================================================
# GAUGES (Gauge)
# ============================================================

MODEL_LOADED = Gauge(
    "model_loaded",
    "Indica se o modelo está carregado (1) ou não (0)",
)

AVG_CONFIDENCE = Gauge(
    "prediction_avg_confidence",
    "Probabilidade média das predições de churn desde a subida da API",
)

# Estado interno para calcular a média cumulativa exposta em
# AVG_CONFIDENCE. Um Gauge só guarda o último valor definido — a
# média em si precisa ser calculada por quem chama .set(), então
# mantemos soma e contagem aqui.
_confidence_sum = 0.0
_confidence_count = 0


def record_prediction_confidence(probability: float) -> None:
    """Atualiza a média cumulativa de confiança das predições.

    Chame esta função uma vez por predição bem-sucedida, passando a
    probabilidade retornada pelo modelo. A média é cumulativa desde
    o último restart da API (reinicia junto com o processo).
    """
    global _confidence_sum, _confidence_count  # noqa: PLW0603

    _confidence_count += 1
    _confidence_sum += probability
    AVG_CONFIDENCE.set(_confidence_sum / _confidence_count)
