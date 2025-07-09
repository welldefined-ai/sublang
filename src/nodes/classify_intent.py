"""Intent classification node for the LangGraph chatbot."""

from typing import Any, Dict
import litellm
from config import config
from ..state import ChatState
from ..prompt_loader import PromptLoader

# Initialize prompt loader
prompt_loader = PromptLoader()

# Configure LiteLLM
litellm.set_verbose = False  # Set to True for debugging


def classify_intent(state: ChatState) -> Dict[str, Any]:
    """Classify the intent of the user's message using LLM.
    
    Args:
        state: Current chat state
        
    Returns:
        Dictionary with classified intent and confidence
    """
    message = state["message"]
    history = state.get("history", [])
    
    # Get the classification prompt
    system_prompt = prompt_loader.get_prompt("CLASSIFY_INTENT")
    
    try:
        # Prepare context for classification
        if history:
            # Get the last assistant response for context
            last_assistant_response = None
            for entry in reversed(history):
                if entry.get("role") == "assistant":
                    last_assistant_response = entry.get("content", "")
                    break
            
            if last_assistant_response:
                user_prompt = f"""Previous assistant response: {last_assistant_response}

Current user message: {message}

Based on the previous response and the new user message, is this conversation still about software design?"""
            else:
                user_prompt = f"""Current user message: {message}

This is the first message in the conversation. Is this about software design?"""
        else:
            user_prompt = f"""Current user message: {message}

This is the first message in the conversation. Is this about software design?"""
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate classification using LiteLLM
        response = litellm.completion(
            messages=messages,
            **config.get_model_params()
        )
        
        classification_result = response.choices[0].message.content.strip()
        
        # Parse the classification result
        if "DESIGN_SPECS" in classification_result.upper():
            intent = "DESIGN_SPECS"
            confidence = "high"
        elif "GENERAL" in classification_result.upper():
            intent = "GENERAL"
            confidence = "high"
        else:
            # Fallback to general if classification is unclear
            intent = "GENERAL"
            confidence = "low"
        
        return {
            "intent": intent,
            "context": {
                **state.get("context", {}),
                "classification_confidence": confidence,
                "classification_method": "llm"
            }
        }
    
    except Exception as e:
        print(f"Error in LLM classification: {e}")
        # Fallback to general on error
        return {
            "intent": "GENERAL",
            "context": {
                **state.get("context", {}),
                "classification_confidence": "low",
                "classification_method": "fallback",
                "error": str(e)
            }
        }