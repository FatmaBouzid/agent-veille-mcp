"""
État partagé du graphe — ce qui circule entre les nœuds.

Pourquoi TypedDict et pas un modèle Pydantic ici : LangGraph utilise
TypedDict comme convention pour l'état du graphe (léger, pas de validation
à chaque transition de nœud — la validation Pydantic, elle, vit dans les
schémas d'input/output des tools, cf. Bloc 10).
"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # add_messages : reducer spécial de LangGraph qui ACCUMULE les messages
    # au lieu de les écraser à chaque passage dans un nœud — indispensable
    # pour garder l'historique de la conversation (question, tool calls,
    # résultats des tools, réponse finale) au fil des cycles ReAct.
    messages: Annotated[list, add_messages]