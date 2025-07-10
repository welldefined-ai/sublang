#!/usr/bin/env python3
"""SubLang Chatbot - LangGraph-based chatbot with predefined prompts."""

import os
from typing import List, Dict
from dotenv import load_dotenv
from .config import config
from .chatbot import create_chatbot, chat_with_bot

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


def get_multiline_input(prompt: str = "You: ") -> str:
    """Get multi-line input from user. Users can paste multi-line text or type across multiple lines.
    
    Input ends when user presses Enter twice on consecutive empty lines, BUT only if those
    empty lines come at the very end (not in the middle of pasted content).
    
    Args:
        prompt: The prompt to display to the user
        
    Returns:
        The complete multi-line input as a string
    """
    print(f"{prompt}(Press Enter twice to finish)")
    lines = []
    
    while True:
        try:
            line = input()
            lines.append(line)
            
            # Check if we have at least 2 lines and the last 2 are empty
            if len(lines) >= 2 and lines[-1] == "" and lines[-2] == "":
                # Remove the two trailing empty lines used for termination
                lines = lines[:-2]
                break
                
        except EOFError:
            break
    
    return '\n'.join(lines)


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
        print("Chatbot ready! Type 'quit' to exit.")
        print("Press Enter twice to finish input.\n")
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        return
    
    # Chat loop
    history: List[Dict[str, str]] = []
    
    while True:
        try:
            user_input = get_multiline_input().strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Show that input is finished and bot is processing
            print("Bot: (Working on it...)", flush=True)
            
            # Get response from chatbot
            result = chat_with_bot(chatbot, user_input, history)
            
            # Print response
            print(result['response'])
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