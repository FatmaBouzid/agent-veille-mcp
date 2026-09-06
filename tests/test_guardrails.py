"""
Teste les guardrails de façon isolée, indépendamment des vrais tools —
avec un schéma et une fonction bidons pour ne dépendre d'aucune logique
métier réelle (RAG, météo).
"""

from pydantic import BaseModel, Field

from agent_veille.guardrails.validators import validate_input, with_fallback


class _DummySchema(BaseModel):
    value: str = Field(..., min_length=3)


def test_validate_input_success():
    result = validate_input(_DummySchema, {"value": "abc"})
    assert isinstance(result, _DummySchema)
    assert result.value == "abc"


def test_validate_input_failure_returns_error_string():
    result = validate_input(_DummySchema, {"value": "ab"})
    assert isinstance(result, str)
    assert "Entrée invalide" in result

def test_with_fallback_returns_result_on_success():
    @with_fallback("erreur générique")
    def always_works() -> str:
        return "ok"

    assert always_works() == "ok"


def test_with_fallback_catches_exception():
    @with_fallback("service indisponible")
    def always_fails() -> str:
        raise RuntimeError("détail")

    result = always_fails()
    assert "service indisponible" in result
    assert "détail" in result