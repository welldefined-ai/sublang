"""Model configuration for the SubLang chatbot."""

import os
import litellm
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class ModelConfig:
    """Model configuration supporting multiple providers via LiteLLM."""
    
    def __init__(self):
        # Default model configuration
        self.model: str = os.getenv("MODEL", "gpt-4o-mini")
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens: Optional[int] = self._get_int_env("MAX_TOKENS")
        
        # API keys (automatically detected by LiteLLM)
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
        self.azure_api_key: Optional[str] = os.getenv("AZURE_API_KEY")
        self.cohere_api_key: Optional[str] = os.getenv("COHERE_API_KEY")
        
        # Provider-specific configurations
        self.azure_api_base: Optional[str] = os.getenv("AZURE_API_BASE")
        self.azure_api_version: Optional[str] = os.getenv("AZURE_API_VERSION")
        
        # Configure LiteLLM globally
        self.configure_litellm()
    
    def configure_litellm(self) -> None:
        """Configure LiteLLM settings globally."""
        litellm.set_verbose = False  # Set to True for debugging
        
    def _get_int_env(self, key: str) -> Optional[int]:
        """Get integer environment variable."""
        value = os.getenv(key)
        return int(value) if value else None
    
    def get_model_params(self) -> dict:
        """Get model parameters for LiteLLM."""
        params = {
            "model": self.model,
            "temperature": self.temperature,
        }
        
        if self.max_tokens:
            params["max_tokens"] = self.max_tokens
            
        return params


# Global config instance
config = ModelConfig()