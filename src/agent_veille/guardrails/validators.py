"""
Guardrails : validation des inputs et fallback propre en cas d'échec d'un tool.

Pourquoi un module séparé des tools eux-mêmes : les tools (rag_tool.py,
external_api_tool.py) restent concentrés sur LEUR logique métier. Ce module
capture la responsabilité transversale "que faire si ça échoue" une seule
fois, réutilisable pour n'importe quel tool actuel ou futur.
"""

from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel, ValidationError

InputSchema = TypeVar("InputSchema", bound=BaseModel)


def validate_input(schema: type[InputSchema], raw_input: dict) -> InputSchema | str:
    """
    Valide raw_input contre le schéma Pydantic donné.

    Retourne soit l'objet validé (succès), soit un message d'erreur str
    (échec) — pattern volontairement simple ("either/or") plutôt qu'une
    exception, car ce message doit pouvoir être renvoyé TEL QUEL au LLM
    comme résultat de tool, sans crasher le graphe LangGraph.
    """
    try:
        return schema(**raw_input)
    except ValidationError as e:
        first_error = e.errors()[0]
        return f"Entrée invalide : {first_error['msg']}"


def with_fallback(fallback_message: str) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """
    Décorateur PARAMÉTRABLE : @with_fallback("message") plutôt que @with_fallback
    seul, car chaque tool a besoin d'un message de repli différent et adapté
    à son contexte (ex: "Impossible de consulter la documentation interne"
    vs "Service météo indisponible").

    Exécute func, et si une exception survient (API down, timeout réseau,
    ChromaDB inaccessible), retourne fallback_message au lieu de crasher.
    """

    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        def wrapper(*args, **kwargs) -> str:
            try:
                return func(*args, **kwargs)
            except Exception as e:  # noqa: BLE001 - volontaire: fallback générique pour tout type de panne de tool
                return f"{fallback_message} (détail technique : {e})"

        return wrapper

    return decorator