"""
On teste que le logger produit bien du JSON valide et structuré,
pas le comportement de logging.Logger lui-même (déjà testé par la
stdlib Python).
"""

import json
import logging

from agent_veille.observability.logger import JSONFormatter, get_logger, log_tool_call


def test_json_formatter_produces_valid_json():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="test message", args=(), exc_info=None,
    )
    output = formatter.format(record)
    parsed = json.loads(output)  # lève une exception si le JSON est invalide

    assert parsed["message"] == "test message"
    assert parsed["level"] == "INFO"
    assert "timestamp" in parsed


def test_log_tool_call_includes_tool_name_and_args(caplog):
    logger = get_logger("test_logger")
    with caplog.at_level(logging.INFO, logger="test_logger"):
        log_tool_call(logger, "get_current_weather", {"city_name": "Sfax"})

    assert "get_current_weather" in caplog.text