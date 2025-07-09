"""Prompt loader for managing chatbot prompts from text files."""

import os
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
        """Load all .txt files from the prompts directory.
        
        Raises:
            FileNotFoundError: If prompts directory doesn't exist
        """
        if not self.prompts_dir.exists():
            raise FileNotFoundError(
                f"Prompts directory '{self.prompts_dir}' not found"
            )
        
        for prompt_file in self.prompts_dir.glob("*.txt"):
            prompt_name = prompt_file.stem.upper()
            with open(prompt_file, 'r', encoding='utf-8') as f:
                self.prompts[prompt_name] = f.read().strip()
    
    def get_prompt(self, intent: str) -> str:
        """Get prompt by intent, fallback to general if not found.
        
        Args:
            intent: Intent name to get prompt for
            
        Returns:
            Prompt text for the given intent
        """
        return self.prompts.get(intent, self.prompts.get('GENERAL', ''))
    
    def reload_prompts(self) -> None:
        """Reload prompts from files (useful for development)."""
        self.prompts.clear()
        self.load_prompts()

# Intent classification keywords
INTENT_KEYWORDS = {
    'DESIGN_SPECS': [
        'design', 'architecture', 'requirements', 'specification', 'specs', 
        'system design', 'software design', 'api design', 'database design',
        'plan', 'structure', 'blueprint', 'schema', 'model'
    ],
}