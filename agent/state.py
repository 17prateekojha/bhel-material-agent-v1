from typing import TypedDict, Any

class AgentState(TypedDict, total=False):
    messages: list[Any]
    result: str
