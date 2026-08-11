import os
from langgraph.prebuilt import create_react_agent
from agent.tools import search_material, find_reconciliation_exceptions, search_by_description
from config import get_setting


def get_model():
    if get_setting("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=get_setting("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
        )

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=get_setting("OLLAMA_MODEL", "qwen2.5:3b"),
        base_url=get_setting("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
    )


def build_agent():
    model = get_model()
    tools = [search_material, find_reconciliation_exceptions, search_by_description]
    return create_react_agent(
        model=model,
        tools=tools,
        prompt=(
            "You are the BHEL TBG HVDC Nagpur Material Management Agent. "
            "Use tools for database facts. Never invent quantities or statuses. "
            "Clearly identify reconciliation exceptions and missing information."
        ),
    )


def ask_agent(question: str) -> str:
    agent = build_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return result["messages"][-1].content
