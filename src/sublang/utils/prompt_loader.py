"""Prompt loader for managing chatbot prompts from text files."""

from pathlib import Path
from typing import Dict


class PromptLoader:
    """Load and manage prompts from text files."""
    
    def __init__(self, prompts_dir: str = "prompts") -> None:
        """Initialize prompt loader.
        
        Args:
            prompts_dir: Directory containing prompt text files
        """
        self.prompts_dir = Path(prompts_dir)
        self.prompts: Dict[str, str] = {}
        self.load_prompts()
    
    def load_prompts(self) -> None:
        """Load all .md files from the prompts directory.
        
        Raises:
            FileNotFoundError: If prompts directory doesn't exist
        """
        if not self.prompts_dir.exists():
            raise FileNotFoundError(
                f"Prompts directory '{self.prompts_dir}' not found"
            )
        
        for prompt_file in self.prompts_dir.glob("*.md"):
            prompt_name = prompt_file.stem.upper()
            with open(prompt_file, 'r', encoding='utf-8') as f:
                self.prompts[prompt_name] = f.read().strip()
    
    def get_prompt(self, intent: str) -> str:
        """Get prompt by intent with dynamic content substitution.
        
        Args:
            intent: Intent name to get prompt for
            
        Returns:
            Prompt text for the given intent
        """
        base_prompt = self.prompts.get(intent, self.prompts.get('GENERAL', ''))
        
        # For GENERAL intent, substitute README content
        if intent == 'GENERAL' and '{readme_section}' in base_prompt:
            readme_content = self._load_readme()
            if readme_content:
                formatted_readme = f"""
## Project Information (Optional Reference)
The following is information about this project. Use this as context when users ask about the project, but for general questions unrelated to this project, just respond normally.

{readme_content}"""
            else:
                formatted_readme = ""
            
            return base_prompt.replace('{readme_section}', formatted_readme)
        
        return base_prompt
    
    def _load_readme(self) -> str:
        """Load README.md content from project root.
        
        Returns:
            README content or empty string if not found
        """
        try:
            readme_path = Path("README.md")
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception as e:
            print(f"Warning: Could not load README.md: {e}")
        return ""
    
    def reload_prompts(self) -> None:
        """Reload prompts from files (useful for development)."""
        self.prompts.clear()
        self.load_prompts()

# Note: Intent classification is now handled by LLM instead of keywords
# The INTENT_KEYWORDS dictionary has been removed as classification is now 
# performed by the LLM using the classify_intent.md prompt
