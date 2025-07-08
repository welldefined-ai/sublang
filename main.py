#!/usr/bin/env python3
"""SubLang Chatbot - LangGraph-based chatbot with predefined prompts."""

import os
from typing import List, Dict
from dotenv import load_dotenv
from config import config
from src.chatbot import create_chatbot, chat_with_bot

# Load environment variables
load_dotenv()


def check_api_keys() -> bool:
    """Check if at least one API key is configured.
    
    Returns:
        True if at least one API key is found
    """
    api_keys = [
        config.openai_api_key,
        config.anthropic_api_key,
        config.google_api_key,
        config.azure_api_key,
        config.cohere_api_key,
    ]
    
    if not any(api_keys):
        print("Error: No API keys found!")
        print("Please set at least one API key in your .env file:")
        print("- OPENAI_API_KEY")
        print("- ANTHROPIC_API_KEY")
        print("- GOOGLE_API_KEY")
        print("- AZURE_API_KEY")
        print("- COHERE_API_KEY")
        return False
    
    return True


def main() -> None:
    """Main function to run the chatbot."""
    # Check API keys
    if not check_api_keys():
        return
    
    # Create the chatbot
    print("Initializing SubLang Chatbot...")
    print(f"Using model: {config.model}")
    
    try:
        chatbot = create_chatbot()
        print("Chatbot ready! Type 'quit' to exit.\n")
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        return
    
    # Chat loop
    history: List[Dict[str, str]] = []
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Get response from chatbot
            result = chat_with_bot(chatbot, user_input, history)
            
            # Print response
            print(f"Bot: {result['response']}")
            print(f"(Intent: {result['intent']})\n")
            
            # Update history
            history = result['history']
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()