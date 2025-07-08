"""Node functions for the LangGraph chatbot."""

from typing import Any, Dict
import litellm
from config import config
from .state import ChatState
from .prompt_loader import PromptLoader, INTENT_KEYWORDS

# Initialize prompt loader
prompt_loader = PromptLoader()

# Configure LiteLLM
litellm.set_verbose = False  # Set to True for debugging


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


def generate_response(state: ChatState) -> Dict[str, Any]:
    """Generate response based on classified intent.
    
    Args:
        state: Current chat state
        
    Returns:
        Dictionary with generated response and updated history
    """
    message = state["message"]
    intent = state["intent"]
    history = state.get("history", [])
    
    # Get the appropriate prompt
    system_prompt = prompt_loader.get_prompt(intent)
    
    try:
        # Build conversation context
        context = ""
        if history:
            # Keep last 6 messages for context
            recent_history = history[-6:]
            context_parts = []
            for entry in recent_history:
                role = entry.get("role", "")
                content = entry.get("content", "")
                context_parts.append(f"{role}: {content}")
            context = "\\n".join(context_parts) + "\\n\\n"
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation history
        if history:
            for entry in history[-6:]:  # Keep last 6 messages for context
                messages.append(entry)
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        # Generate response using LiteLLM
        response = litellm.completion(
            messages=messages,
            **config.get_model_params()
        )
        
        response_content = response.choices[0].message.content
        
        return {
            "response": response_content,
            "history": history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response_content}
            ]
        }
    
    except Exception as e:
        print(f"Error generating response: {e}")
        error_msg = (
            "I apologize, but I encountered an error while processing "
            "your request. Please try again."
        )
        return {
            "response": error_msg,
            "history": history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": "Error occurred"}
            ]
        }