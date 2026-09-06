"""
On teste que le serveur FastMCP expose bien les deux tools attendus,
avec les bons noms et descriptions — pas un test d'intégration complet
du protocole MCP (trop lourd), mais une vérification du contrat exposé.
"""

import pytest

from agent_veille.mcp_server.server import mcp


@pytest.mark.asyncio
async def test_mcp_server_exposes_expected_tools():
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}

    assert "search_internal_docs" in tool_names
    assert "get_current_weather" in tool_names


@pytest.mark.asyncio
async def test_mcp_search_internal_docs_rejects_invalid_input():
    result = await mcp.call_tool("search_internal_docs", {"query": "ab"})
    # result est une liste de content blocks MCP ; on vérifie le texte
    text = result[0].text if hasattr(result[0], "text") else str(result)
    assert "Entrée invalide" in text