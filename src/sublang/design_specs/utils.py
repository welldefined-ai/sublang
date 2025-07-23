"""Utility functions for design specs nodes."""

import re
from typing import Optional


def parse_markdown_code_block(response: str) -> Optional[str]:
    """Extract content from the last markdown code block in a response.

    Args:
        response: The full response text that may contain code blocks

    Returns:
        The content of the last code block, or None if no code block found
    """
    # Pattern to match code blocks with triple backticks
    # Captures content between ``` and ```
    pattern = r'```(?:\w*\n)?(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)

    if matches:
        # Return the last code block found (as per the prompts, the final output should be in a code block)
        return matches[-1].strip()

    return None


def combine_prompts(overall_prompt: str, specific_prompt: str) -> str:
    """Combine the overall.md prompt with a step-specific prompt.

    Args:
        overall_prompt: Content of overall.md
        specific_prompt: Content of step-specific prompt (extract_terms.md, etc.)

    Returns:
        Combined prompt with overall context followed by specific instructions
    """
    return f"{overall_prompt}\n\n---\n\n{specific_prompt}"
