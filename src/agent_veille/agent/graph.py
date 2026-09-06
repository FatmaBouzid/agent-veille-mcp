"""
Construction du graphe LangGraph — pattern ReAct manuel.

Flow :
  START -> agent_node -> (a-t-il appelé un tool ?)
              |                    |
              | non                | oui
              v                    v
             END              tool_node -> agent_node (boucle)

Pourquoi une boucle (agent -> tool -> agent) et pas juste agent -> tool -> END :
après avoir observé le résultat d'un tool, le LLM doit pouvoir soit répondre
directement, soit décider d'appeler un DEUXIÈME tool si la question le
nécessite (ex: "quelle est la doc LangGraph et la météo à Sfax ?").
"""

from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agent_veille.agent.prompts import SYSTEM_PROMPT
from agent_veille.agent.state import AgentState
from agent_veille.config import settings
from agent_veille.tools.external_api_tool import get_current_weather
from agent_veille.tools.rag_tool import search_internal_docs

TOOLS = [search_internal_docs, get_current_weather]


def _build_llm() -> ChatGroq:
    """
    Instancie le LLM Groq avec les tools attachés.

    bind_tools() est ce qui active le function calling : le LLM reçoit le
    schéma (nom, description, arguments) de chaque tool et peut décider d'en
    appeler un en renvoyant un "tool_call" structuré plutôt qu'un texte libre.
    """
    llm = ChatGroq(model=settings.llm_model_name, api_key=settings.groq_api_key)
    return llm.bind_tools(TOOLS)


def agent_node(state: AgentState) -> dict:
    """
    Nœud "raisonnement" : le LLM lit l'historique et décide de répondre
    directement OU d'appeler un tool.
    """
    llm = _build_llm()
    messages = state["messages"]

    # Injecte le prompt système seulement s'il n'est pas déjà présent
    # (évite de le dupliquer à chaque cycle de la boucle ReAct).
    if not messages or messages[0].type != "system":
        from langchain_core.messages import SystemMessage
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """
    Arête conditionnelle : décide si on continue vers un tool ou si on
    termine le graphe.

    On regarde le DERNIER message émis par le LLM : s'il contient des
    tool_calls, LangGraph route vers tool_node ; sinon, vers END.
    """
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


def build_graph():
    """Assemble le graphe complet et le compile en objet exécutable."""
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")  # après un tool, on repasse par le raisonnement

    return graph.compile()