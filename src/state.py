"""State definition for the chatbot."""

from typing import Dict, List
from typing_extensions import TypedDict


class ChatState(TypedDict):
    """State structure for the chatbot conversation."""
    message: str
    history: List[Dict[str, str]]
    intent: str
    response: str
    context: Dict[str, str]