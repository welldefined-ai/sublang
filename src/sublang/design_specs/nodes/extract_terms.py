"""Extract terms from user requirements for design specifications."""

from typing import Any, Dict
import litellm
from pathlib import Path
from sublang.utils import config, PromptLoader

# Initialize prompt loader for design_specs subgraph
prompt_loader = PromptLoader(str(Path(__file__).parent.parent / "prompts"))


def extract_terms(state) -> Dict[str, Any]:
    """Extract key terms from user-provided descriptions.
    
    Args:
        state: Current chat state
        
    Returns:
        Dictionary with extracted terms and updated history
    """
    message = state["message"]
    history = state.get("history", [])
    
    # Get the terms extraction prompt
    system_prompt = prompt_loader.get_prompt("EXTRACT_TERMS")
    
    try:
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation history (last 4 messages = 2 rounds of talk)
        # Only the first step gets the conversation history
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
            "terms": response_content,
            "intent": "DESIGN_SPECS",
            "history": history  # Don't add to history - this is internal processing
        }
    
    except Exception as e:
        print(f"Error extracting terms: {e}")
        error_msg = (
            "I apologize, but I encountered an error while extracting "
            "terms from your description. Please try again."
        )
        return {
            "terms": error_msg,
            "intent": "DESIGN_SPECS",
            "history": history  # Don't add to history - this is internal processing
        }
