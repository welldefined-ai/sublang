"""General response generation node for the LangGraph chatbot."""

from typing import Any, Dict
import litellm
from ..config import config
from ..state import ChatState
from ..prompt_loader import PromptLoader

# Initialize prompt loader
prompt_loader = PromptLoader()

# Configure LiteLLM
litellm.set_verbose = False  # Set to True for debugging


def generate_response(state: ChatState) -> Dict[str, Any]:
    """Generate general response for non-design queries.
    
    Args:
        state: Current chat state
        
    Returns:
        Dictionary with generated response and updated history
    """
    message = state["message"]
    history = state.get("history", [])
    
    # Get the general prompt (includes README content automatically)
    system_prompt = prompt_loader.get_prompt("GENERAL")
    
    try:
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation history (last 4 messages = 2 rounds of talk)
        if history:
            for entry in history[-4:]:  # Keep last 4 messages for context
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
            "intent": "GENERAL",
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
            "intent": "GENERAL",
            "history": history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": "Error occurred"}
            ]
        }