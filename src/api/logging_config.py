"""Configuração de logs estruturados (JSON).

Logs em formato de texto simples dificultam filtragem, agregação e
correlação de eventos de uma mesma requisição. Este módulo configura
um logger que emite cada registro como uma linha JSON, com campos
padronizados (timestamp, level, service, logger) presentes em todo
log, além dos campos extras que cada chamada de log declarar.

Isso facilita a análise em ferramentas de observabilidade (CloudWatch,
Kibana, Loggly, ELK) e permite consultas estruturadas, como filtrar
por trace_id, endpoint ou status_code.

Exemplo de uso:
    from src.api.logging_config import logger

    logger.info("prediction_completed", extra={
        "trace_id": trace_id,
        "prediction": 1,
        "probability": 0.87,
    })

Saída:
    {"timestamp": "2026-09-23T21:04:00Z", "level": "INFO",
     "service": "churn-prediction-api", "logger": "api",
     "message": "prediction_completed", "trace_id": "a1b2c3d4",
     "prediction": 1, "probability": 0.87}
"""

import logging
import os
import sys
from datetime import datetime, timezone

from pythonjsonlogger import jsonlogger

from src import environment as environment  # Load .env before resolving LOG_LEVEL.

SERVICE_NAME = "churn-prediction-api"


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Formatter que adiciona campos padrão a cada linha de log.

    Campos adicionados automaticamente:
        timestamp: data/hora em formato ISO 8601 (UTC).
        level: nível do log (INFO, WARNING, ERROR).
        service: nome do serviço, para diferenciar logs quando
            vários serviços compartilham o mesmo agregador.
        logger: nome do logger que emitiu o registro.
    """

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        log_record["timestamp"] = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        log_record["level"] = record.levelname
        log_record["service"] = SERVICE_NAME
        log_record["logger"] = record.name

        if not log_record.get("message"):
            log_record["message"] = record.getMessage()


def setup_logging(level: str | None = None) -> logging.Logger:
    """Configura e retorna o logger estruturado da aplicação.

    Args:
        level: Nível mínimo de log (DEBUG, INFO, WARNING, ERROR).
            Se omitido, usa a variável de ambiente LOG_LEVEL,
            com "INFO" como padrão.

    Returns:
        Logger configurado para emitir JSON em stdout.

    Nota de segurança: nunca passe dados sensíveis (senhas, tokens,
    CPF, e-mail) como campo `extra` — eles vão parar no log em texto
    claro. Registre identificadores não sensíveis (username, role,
    trace_id) e resultados agregados (classe prevista, latência).
    """
    resolved_level = level or os.getenv("LOG_LEVEL", "INFO")

    logger_instance = logging.getLogger("api")
    logger_instance.setLevel(getattr(logging, resolved_level.upper()))

    # Handler para stdout: containers (Docker, Render, etc.) capturam
    # stdout/stderr automaticamente, sem precisar gerenciar arquivos
    # de log dentro do container.
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    )

    # Remove handlers anteriores para evitar log duplicado caso
    # setup_logging seja chamado mais de uma vez (ex.: em testes).
    logger_instance.handlers = []
    logger_instance.addHandler(handler)
    logger_instance.propagate = False

    return logger_instance


# Logger global: importe `from src.api.logging_config import logger`
# em qualquer módulo que precise registrar eventos.
logger = setup_logging()
