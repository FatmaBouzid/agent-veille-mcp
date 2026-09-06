"""
Serveur MCP exposant les tools de l'agent (RAG interne + météo) via le
protocole Model Context Protocol.

Pourquoi ré-exposer ici plutôt que d'importer directement les objets @tool
de LangChain : les deux frameworks ont des décorateurs différents
(@tool de LangChain vs @mcp.tool() de FastMCP) qui produisent des objets
de nature différente (StructuredTool vs fonction MCP). On réutilise la
LOGIQUE (les fonctions _impl, déjà validées et avec fallback via les
guardrails du Bloc 10) sans dépendre de l'objet LangChain lui-même.
"""

from mcp.server.fastmcp import FastMCP

from agent_veille.guardrails.validators import validate_input
from agent_veille.tools.external_api_tool import _get_current_weather_impl
from agent_veille.tools.rag_tool import _search_internal_docs_impl
from agent_veille.tools.schemas import SearchDocsInput, WeatherInput

mcp = FastMCP("agent-veille-mcp")


@mcp.tool()
def search_internal_docs(query: str) -> str:
    """
    Recherche des informations dans la base de connaissances interne
    (documents techniques indexés : LangGraph, MCP, RAG, etc.).
    """
    validated = validate_input(SearchDocsInput, {"query": query})
    if isinstance(validated, str):
        return validated
    return _search_internal_docs_impl(validated.query)


@mcp.tool()
def get_current_weather(city_name: str) -> str:
    """
    Donne la météo actuelle (température, vent) pour une ville donnée.
    """
    validated = validate_input(WeatherInput, {"city_name": city_name})
    if isinstance(validated, str):
        return validated
    return _get_current_weather_impl(validated.city_name)


if __name__ == "__main__":
    # transport stdio : mode standard pour un serveur MCP local, lu par
    # un client (Claude Desktop, un autre agent) via son entrée/sortie standard
    mcp.run(transport="stdio")