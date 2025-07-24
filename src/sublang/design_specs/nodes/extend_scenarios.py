"""Extend use scenarios from user requirements for design specifications."""

from typing import Any, Dict
import litellm
from pathlib import Path
from sublang.utils import config, PromptLoader
from sublang.design_specs.utils import combine_prompts, parse_markdown_code_block

# Initialize prompt loader for design_specs subgraph
prompt_loader = PromptLoader(str(Path(__file__).parent.parent / "prompts"))


def extend_scenarios(state) -> Dict[str, Any]:
    """Extend user description by adding comprehensive use scenarios.

    Args:
        state: Current chat state

    Returns:
        Dictionary with extended scenarios and updated state
    """
    message = state["message"]
    history = state.get("history", [])

    # Get the overall prompt and scenario extension prompt
    overall_prompt = prompt_loader.get_prompt("OVERALL")
    extend_scenarios_prompt = prompt_loader.get_prompt("EXTEND_SCENARIOS")
    system_prompt = combine_prompts(overall_prompt, extend_scenarios_prompt)

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

        # Parse the markdown code block from the response
        parsed_scenarios = parse_markdown_code_block(response_content)

        # Use parsed scenarios if found, otherwise use the full response
        scenarios_output = parsed_scenarios if parsed_scenarios else response_content

        return {
            "message": scenarios_output,  # Replace original message with extended scenarios
            "intent": "DESIGN_SPECS",
            "history": history  # Don't add to history - this is internal processing
        }

    except Exception as e:
        print(f"Error extending scenarios: {e}")
        error_msg = (
            "I apologize, but I encountered an error while extending "
            "use scenarios from your description. Using original description."
        )
        # On error, keep the original message
        return {
            "message": message,
            "intent": "DESIGN_SPECS",
            "history": history  # Don't add to history - this is internal processing
        }