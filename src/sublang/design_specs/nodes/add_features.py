"""Add features to design specifications based on terms and descriptions."""

from typing import Any, Dict
import litellm
from pathlib import Path
from sublang.utils import config, PromptLoader
from sublang.design_specs.utils import combine_prompts, parse_markdown_code_block

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

    # Get the overall prompt and features addition prompt
    overall_prompt = prompt_loader.get_prompt("OVERALL")
    add_features_prompt = prompt_loader.get_prompt("ADD_FEATURES")
    system_prompt = combine_prompts(overall_prompt, add_features_prompt)

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

        # Parse the markdown code block from the response
        parsed_features = parse_markdown_code_block(response_content)

        # Use parsed features if found, otherwise use the full response
        features_output = parsed_features if parsed_features else response_content

        return {
            "features": features_output,
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
