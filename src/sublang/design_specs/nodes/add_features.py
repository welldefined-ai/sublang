"""Add features to design specifications based on terms and descriptions."""

from typing import Any, Dict
import litellm
from pathlib import Path
from sublang.utils import config, PromptLoader

# Initialize prompt loader for design_specs subgraph
prompt_loader = PromptLoader(str(Path(__file__).parent.parent / "prompts"))


def add_features(state) -> Dict[str, Any]:
    """Add features based on description and terms, adjusting terms if necessary.
    
    Args:
        state: Current chat state
        
    Returns:
        Dictionary with features and potentially adjusted terms
    """
    message = state["message"]
    terms = state.get("terms", "")
    history = state.get("history", [])
    
    # Get the features addition prompt
    system_prompt = prompt_loader.get_prompt("ADD_FEATURES")
    
    try:
        # Create messages for the LLM - no history needed for internal processing
        user_message = f"Original description: {message}\n\nPreviously extracted terms:\n{terms}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Generate response using LiteLLM
        response = litellm.completion(
            messages=messages,
            **config.get_model_params()
        )
        
        response_content = response.choices[0].message.content
        
        return {
            "features": response_content,
            "intent": "DESIGN_SPECS",
            "history": history  # Don't add to history - this is internal processing
        }
    
    except Exception as e:
        print(f"Error adding features: {e}")
        error_msg = (
            "I apologize, but I encountered an error while adding "
            "features to your design. Please try again."
        )
        return {
            "features": error_msg,
            "intent": "DESIGN_SPECS",
            "history": history  # Don't add to history - this is internal processing
        }