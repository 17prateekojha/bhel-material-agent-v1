from langgraph.prebuilt import create_react_agent

from agent.tools import (
    search_material,
    search_materials_received_today,
    find_reconciliation_exceptions,
    search_by_description,
)
from config import get_setting


def get_model():
    """
    Select the AI provider.

    Cloud:
        Uses Groq when GROQ_API_KEY is configured.

    Local:
        Falls back to Ollama when no Groq API key is configured.
    """

    groq_api_key = get_setting("GROQ_API_KEY")

    if groq_api_key:
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=get_setting(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile",
            ),
            temperature=0,
            api_key=groq_api_key,
        )

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=get_setting(
            "OLLAMA_MODEL",
            "qwen2.5:3b",
        ),
        base_url=get_setting(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        ),
        temperature=0,
    )


def build_agent():
    model = get_model()

    tools = [
        search_material,
        search_materials_received_today,
        find_reconciliation_exceptions,
        search_by_description,
    ]

    return create_react_agent(
        model=model,
        tools=tools,
        prompt=(
            "You are the BHEL TBG HVDC Nagpur Material Management Agent. "

            "Use tools for database facts. Never invent quantities, dates, "
            "material IDs, suppliers, or statuses. "

            "IMPORTANT TOOL RULES: "

            "For questions asking about materials received today, "
            "call search_materials_received_today exactly once. "
            "Do not call search_by_description for today's receipt questions. "

            "For a specific Material ID, call search_material exactly once. "

            "For description, item code, PO number, or supplier searches, "
            "call search_by_description. "

            "For reconciliation issues or exceptions, "
            "call find_reconciliation_exceptions. "

            "After receiving a tool result, answer the user directly. "
            "Do not repeatedly call the same tool. "

            "If the tool returns no records, clearly say that no matching "
            "records were found."
        ),
    )


def ask_agent(question: str) -> str:
    agent = build_agent()

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    return result["messages"][-1].content