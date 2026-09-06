"""
Teste que la config est stricte (plante sans clé Groq) et que les valeurs
par défaut du RAG/météo sont correctement appliquées.
"""

import pytest
from pydantic import ValidationError

from agent_veille.config import Settings


def test_settings_loads_with_groq_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-test")
    settings = Settings(_env_file=None)
    assert settings.groq_api_key == "fake-key-for-test"
    assert settings.llm_model_name == "openai/gpt-oss-120b"
    assert settings.embedding_model_name == "sentence-transformers/all-MiniLM-L6-v2"


def test_settings_fails_without_groq_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_model_name_overridable(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-test")
    monkeypatch.setenv("LLM_MODEL_NAME", "qwen/qwen3.6-27b")
    settings = Settings(_env_file=None)
    assert settings.llm_model_name == "qwen/qwen3.6-27b"
