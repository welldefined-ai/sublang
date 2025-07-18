"""Add constraints to design specifications based on terms and features."""

from typing import Any, Dict
import litellm
from pathlib import Path
from sublang.utils import config, PromptLoader

# Initialize prompt loader for design_specs subgraph
prompt_loader = PromptLoader(str(Path(__file__).parent.parent / "prompts"))


def add_constraints(state) -> Dict[str, Any]:
    """Add constraints based on terms and features, adjusting them if necessary.
    
    Args:
        state: Current chat state
        
    Returns:
        Dictionary with complete design response including constraints
    """
    message = state["message"]
    terms = state.get("terms", "")
    features = state.get("features", "")
    history = state.get("history", [])
    
    # Get the constraints addition prompt
    system_prompt = prompt_loader.get_prompt("ADD_CONSTRAINTS")
    
    try:
        # Create messages for the LLM - no history needed for internal processing
        user_message = f"Original description: {message}\n\nTerms:\n{terms}\n\nFeatures:\n{features}"
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
            "response": response_content,
            "intent": "DESIGN_SPECS",
            # Only the final step adds to history - the complete conversation
            "history": history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response_content}
            ]
        }
    
    except Exception as e:
        print(f"Error adding constraints: {e}")
        error_msg = (
            "I apologize, but I encountered an error while adding "
            "constraints to your design. Please try again."
        )
        return {
            "response": error_msg,
            "intent": "DESIGN_SPECS",
            # Only the final step adds to history - even for errors
            "history": history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": error_msg}
            ]
        }