"""
On mocke ChatGroq pour ne pas dépendre d'un vrai appel réseau/quota Groq
dans les tests automatisés (rapide, déterministe, marche sans clé en CI
si besoin — mais ici on a quand même besoin d'une clé factice pour Settings).
"""

from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage

from agent_veille.agent.graph import build_graph


@patch("agent_veille.agent.graph.ChatGroq")
def test_agent_answers_without_tool(mock_chat_groq, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")

    # simule un LLM qui répond directement, sans tool_calls
    mock_llm_instance = MagicMock()
    mock_llm_instance.bind_tools.return_value.invoke.return_value = AIMessage(
        content="Bonjour ! Je vais bien, merci."
    )
    mock_chat_groq.return_value = mock_llm_instance

    graph = build_graph()
    result = graph.invoke({"messages": [HumanMessage(content="Bonjour")]})

    assert "Bonjour" in result["messages"][-1].content

def _mock_response(json_data: dict) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.raise_for_status.return_value = None
    return mock

@patch("agent_veille.agent.graph.ChatGroq")
def test_agent_routes_to_tool_when_tool_call_present(mock_chat_groq, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")

    tool_call_message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_current_weather",
                "args": {"city_name": "Sfax"},
                "id": "call_123",
            }
        ],
    )
    final_message = AIMessage(content="Il fait 28°C à Sfax.")

    mock_llm_instance = MagicMock()
    mock_llm_instance.bind_tools.return_value.invoke.side_effect = [
        tool_call_message,
        final_message,
    ]
    mock_chat_groq.return_value = mock_llm_instance

    with patch("agent_veille.tools.external_api_tool.httpx.get") as mock_get:
        mock_get.side_effect = [
            _mock_response({"results": [{"latitude": 34.74, "longitude": 10.76}]}),
            _mock_response({"current": {"temperature_2m": 28.0, "wind_speed_10m": 12.0}}),
        ]

        graph = build_graph()
        result = graph.invoke({"messages": [HumanMessage(content="Météo à Sfax ?")]})

    assert "28°C" in result["messages"][-1].content