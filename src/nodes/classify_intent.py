"""Intent classification node for the LangGraph chatbot."""

from typing import Any, Dict
from ..state import ChatState
from ..prompt_loader import INTENT_KEYWORDS


def classify_intent(state: ChatState) -> Dict[str, Any]:
    """Classify the intent of the user's message.
    
    Args:
        state: Current chat state
        
    Returns:
        Dictionary with classified intent and confidence
    """
    message = state["message"].lower()
    
    # Check for intent keywords
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in message for keyword in keywords):
            return {
                "intent": intent,
                "context": {
                    **state.get("context", {}),
                    "classification_confidence": "high"
                }
            }
    
    # Default to general if no specific intent detected
    return {
        "intent": "GENERAL",
        "context": {
            **state.get("context", {}),
            "classification_confidence": "low"
        }
    }