"""Design specifications generation node for the LangGraph chatbot."""

from typing import Any, Dict
import litellm
from ...config import config
from ...prompt_loader import PromptLoader
from pathlib import Path

# Initialize prompt loader for design_specs subgraph
_current_dir = Path(__file__).parent.parent
prompt_loader = PromptLoader(str(_current_dir / "prompts"))



def design_specs(state) -> Dict[str, Any]:
    """Generate software design specifications and architecture guidance.
    
    Args:
        state: Current chat state
        
    Returns:
        Dictionary with generated design response and updated history
    """
    message = state["message"]
    history = state.get("history", [])
    
    # Get the design specs prompt
    system_prompt = prompt_loader.get_prompt("DESIGN_SPECS")
    
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
            "intent": "DESIGN_SPECS",
            "history": history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response_content}
            ]
        }
    
    except Exception as e:
        print(f"Error generating design specs: {e}")
        error_msg = (
            "I apologize, but I encountered an error while processing "
            "your design request. Please try again."
        )
        return {
            "response": error_msg,
            "intent": "DESIGN_SPECS",
            "history": history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": "Error occurred"}
            ]
        }