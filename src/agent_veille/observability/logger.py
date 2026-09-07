"""
Logging structuré (JSON) pour tracer les décisions de l'agent : quel tool
est appelé, avec quels arguments, et le résultat obtenu.

Pourquoi JSON plutôt que du texte libre : chaque ligne de log devient une
entrée structurée et interrogeable (ex: "montre-moi tous les appels à
get_current_weather qui ont échoué"), contrairement à du texte qu'il
faudrait parser avec des regex fragiles.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formatte chaque log en une ligne JSON plutôt qu'en texte brut."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # les champs extra passés via logger.info(..., extra={...}) sont fusionnés
        if hasattr(record, "tool_name"):
            log_entry["tool_name"] = record.tool_name
        if hasattr(record, "tool_args"):
            log_entry["tool_args"] = record.tool_args
        return json.dumps(log_entry, ensure_ascii=False)


def get_logger(name: str = "agent_veille") -> logging.Logger:
    """
    Instancie un logger configuré pour sortir du JSON sur stdout.

    Pourquoi une fonction plutôt qu'un logger global unique : permet de
    nommer différemment les logs selon leur origine (agent.graph,
    tools.rag_tool, etc.) tout en gardant le même format JSON partout.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:  # évite les doublons si get_logger est appelé plusieurs fois
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_tool_call(logger: logging.Logger, tool_name: str, tool_args: dict) -> None:
    """Log structuré d'un appel de tool — utilisé dans agent_node."""
    logger.info(
        f"Tool appelé : {tool_name}",
        extra={"tool_name": tool_name, "tool_args": tool_args},
    )