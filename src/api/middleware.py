"""Middleware de logging automático de requisições HTTP.

Um middleware roda antes e depois de cada requisição, permitindo
instrumentar toda a API em um único lugar, sem alterar cada endpoint
individualmente. Este middleware:

- Gera um `trace_id` único por requisição, propagado em
  `request.state.trace_id` (disponível para os endpoints, caso
  precisem correlacionar seus próprios logs) e no header de resposta
  `X-Trace-ID` (disponível para o cliente reportar um problema).
- Mede a latência da requisição.
- Registra um log estruturado ao final de cada requisição, com
  método, caminho, status_code, latência e IP do cliente.

O trace_id é o que permite reconstruir toda a jornada de uma
requisição (autenticação -> predição -> resposta) buscando por um
único identificador nos logs, mesmo que ela passe por várias funções.
"""

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.logging_config import logger

# Endpoints excluídos do log de acesso: são chamados com muita
# frequência por infraestrutura (orquestrador de containers, load
# balancer, scrape do Prometheus a cada 15s) e não agregam valor de
# auditoria, apenas ruído.
PATHS_SEM_LOG_DE_ACESSO = {"/health", "/metrics"}


class LoggingMiddleware(BaseHTTPMiddleware):
    """Loga automaticamente toda requisição que chega à API.

    Fluxo:
        1. Requisição chega; gera-se um trace_id.
        2. A requisição é processada normalmente pelo endpoint.
        3. Calcula-se a latência e registra-se o log estruturado.
        4. A resposta segue com os headers X-Trace-ID e
           X-Response-Time-Ms adicionados.
    """

    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())[:8]
        request.state.trace_id = trace_id

        start_time = time.perf_counter()
        response = await call_next(request)
        latency_ms = (time.perf_counter() - start_time) * 1000

        if request.url.path not in PATHS_SEM_LOG_DE_ACESSO:
            logger.info(
                "request_completed",
                extra={
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "latency_ms": round(latency_ms, 2),
                    "client_ip": (
                        request.client.host if request.client else None
                    ),
                },
            )

        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Response-Time-Ms"] = str(round(latency_ms, 2))

        return response
