from langchain_core.tools import tool

from agent_veille.guardrails.validators import validate_input, with_fallback
from agent_veille.rag.retriever import retrieve
from agent_veille.tools.schemas import SearchDocsInput


@with_fallback("Impossible de consulter la base de connaissances interne pour le moment.")
def _search_internal_docs_impl(query: str) -> str:
    chunks = retrieve(query, k=3)
    if not chunks:
        return "Aucun document pertinent trouvé dans la base de connaissances."
    return "\n\n---\n\n".join(chunks)


@tool
def search_internal_docs(query: str) -> str:
    """
    Recherche des informations dans la base de connaissances interne
    (documents techniques indexés : LangGraph, MCP, RAG, etc.).
    Utilise ce tool pour toute question portant sur des concepts techniques
    ou des documents que l'utilisateur a fournis, PAS pour des questions
    sur l'actualité, la météo, ou des faits en temps réel.
    """
    validated = validate_input(SearchDocsInput, {"query": query})
    if isinstance(validated, str):
        return validated  # message d'erreur de validation

    return _search_internal_docs_impl(validated.query)