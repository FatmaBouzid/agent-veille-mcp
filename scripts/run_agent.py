"""Point d'entrée CLI pour tester l'agent en conditions réelles."""

from langchain_core.messages import HumanMessage

from agent_veille.agent.graph import build_graph


def main():
    graph = build_graph()

    print("Agent de veille — tape 'quit' pour sortir.\n")
    while True:
        question = input("Toi : ")
        if question.lower() in {"quit", "exit"}:
            break

        result = graph.invoke({"messages": [HumanMessage(content=question)]})
        final_message = result["messages"][-1]
        print(f"Agent : {final_message.content}\n")


if __name__ == "__main__":
    main()