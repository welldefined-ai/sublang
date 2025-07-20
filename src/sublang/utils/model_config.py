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
        max_tokens_env = os.getenv("MAX_TOKENS")
        self.max_tokens: Optional[int] = int(max_tokens_env) if max_tokens_env else None
        
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
    
    @staticmethod
    def configure_litellm() -> None:
        """Configure LiteLLM settings globally."""
        litellm.set_verbose = False  # Set to True for debugging

        # Setup LangFuse tracing if enabled
        if (os.getenv("LANGFUSE_TRACING", "false").lower() == "true" and
            os.getenv("LANGFUSE_PUBLIC_KEY") and
            os.getenv("LANGFUSE_SECRET_KEY")):
            try:
                # Set both success and failure callbacks as recommended by LiteLLM docs
                litellm.success_callback = ["langfuse"]
                litellm.failure_callback = ["langfuse"]
                print("LangFuse tracing enabled for LiteLLM")
            except Exception as e:
                print(f"Warning: Failed to enable LangFuse tracing: {e}")

    def get_model_params(self) -> dict:
        """Get model parameters for LiteLLM."""
        params = {
            "model": self.model,
            "temperature": self.temperature,
        }
        
        if self.max_tokens:
            params["max_tokens"] = self.max_tokens
            
        return params


def get_langfuse_config():
    """Get LangFuse configuration for LangGraph if tracing is enabled."""
    if (os.getenv("LANGFUSE_TRACING", "false").lower() == "true" and
        os.getenv("LANGFUSE_PUBLIC_KEY") and
        os.getenv("LANGFUSE_SECRET_KEY")):
        try:
            from langfuse.callback import CallbackHandler
            langfuse_handler = CallbackHandler(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            )
            return {"callbacks": [langfuse_handler]}
        except ImportError:
            print("Warning: LangFuse not installed. Install with: pip install langfuse")
            return {}
        except Exception as e:
            print(f"Warning: Failed to setup LangFuse for LangGraph: {e}")
            return {}
    return {}


# Global config instance
config = ModelConfig()
