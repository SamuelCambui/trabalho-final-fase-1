# syntax=docker/dockerfile:1
#
# Dockerfile da Customer Churn Prediction API.
#
# Estratégia de camadas: copiamos primeiro só pyproject.toml + uv.lock
# e instalamos as dependências antes de copiar o código-fonte. Assim,
# o Docker reaproveita a camada de dependências em rebuilds futuros
# sempre que só o código (não as dependências) mudar — evitando
# reinstalar tudo a cada `docker build`.
#
# O modelo treinado (notebooks/models/champion_model.joblib) NÃO é
# copiado para dentro da imagem: o .dockerignore já exclui *.joblib
# de propósito (comentário original: "serão montados via volume").
# Este Dockerfile respeita essa decisão — o volume é montado pelo
# docker-compose.yml, não pela imagem.

FROM python:3.13-slim

# curl é necessário só para o HEALTHCHECK abaixo checar /health.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Instala o uv (mesmo gerenciador de pacotes usado no desenvolvimento
# local), copiando o binário oficial em vez de instalar via pip.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# 1) Camada de dependências: só os arquivos que as declaram.
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# 2) Camada de código: agora sim o projeto em si.
COPY src/ ./src/
COPY README.md ./
RUN uv sync --no-dev

EXPOSE 8000

# O orquestrador (Docker Compose, Kubernetes, etc.) usa isso para
# saber se o container está pronto para receber tráfego — ver
# capítulo de monitoramento: distinção entre liveness e readiness.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
