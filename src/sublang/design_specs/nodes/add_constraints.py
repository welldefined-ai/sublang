"""Add constraints to design specifications based on terms and features."""

from typing import Any, Dict
import litellm
from pathlib import Path
from sublang.utils import config, PromptLoader
from sublang.design_specs.utils import combine_prompts, parse_markdown_code_block

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
    specs = state.get("specs", "")  # Contains terms and features from previous steps
    history = state.get("history", [])

    # Get the overall prompt and constraints addition prompt
    overall_prompt = prompt_loader.get_prompt("OVERALL")
    add_constraints_prompt = prompt_loader.get_prompt("ADD_CONSTRAINTS")
    system_prompt = combine_prompts(overall_prompt, add_constraints_prompt)

    try:
        # Create messages for the LLM - no history needed for internal processing
        # Note: specs already contains terms and features from previous steps
        user_message = f"Original description:\n{message}\n\n---\n\nTerms and Features from previous steps:\n{specs}"
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
        parsed_constraints = parse_markdown_code_block(response_content)

        # Use parsed constraints if found, otherwise use the full response
        final_output = parsed_constraints if parsed_constraints else response_content

        return {
            "response": final_output,
            "intent": "DESIGN_SPECS",
            # Only the final step adds to history - the complete conversation
            "history": history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": final_output}
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
