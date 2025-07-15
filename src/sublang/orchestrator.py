"""Main chatbot orchestrator using subgraphs."""

from typing import Dict, List, Optional, Any
import litellm
from .config import config
from langgraph.graph import StateGraph, START, END
from .state import ChatState
from .chatbot.chatbot import create_chatbot_subgraph, chat_with_bot as chatbot_chat
from .design_specs.design_specs import create_design_specs_subgraph, process_design_request
from .prompt_loader import PromptLoader
from pathlib import Path

# Initialize prompt loader for classification (using chatbot prompts)
_chatbot_prompts_dir = Path(__file__).parent / "chatbot" / "prompts"
prompt_loader = PromptLoader(str(_chatbot_prompts_dir))



def classify_and_route(state: ChatState) -> str:
    """Classify intent and route to appropriate subgraph using LLM.
    
    Args:
        state: Current chat state
        
    Returns:
        Subgraph name to route to ("chatbot" or "design_specs")
    """
    message = state["message"]
    history = state.get("history", [])
    
    # Get the classification prompt
    system_prompt = prompt_loader.get_prompt("CLASSIFY_INTENT")
    
    try:
        # Prepare context for classification
        if history:
            # Get the last assistant response for context
            last_assistant_response = None
            for entry in reversed(history):
                if entry.get("role") == "assistant":
                    last_assistant_response = entry.get("content", "")
                    break
            
            if last_assistant_response:
                user_prompt = f"""Previous assistant response: {last_assistant_response}

Current user message: {message}

Based on the previous response and the new user message, is this conversation still about software design?"""
            else:
                user_prompt = f"""Current user message: {message}

This is the first message in the conversation. Is this about software design?"""
        else:
            user_prompt = f"""Current user message: {message}

This is the first message in the conversation. Is this about software design?"""
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate classification using LiteLLM
        response = litellm.completion(
            messages=messages,
            **config.get_model_params()
        )
        
        classification_result = response.choices[0].message.content.strip()
        
        # Parse the classification result and return route
        if "DESIGN_SPECS" in classification_result.upper():
            return "design_specs"
        else:
            return "chatbot"
    
    except Exception as e:
        print(f"Error in LLM classification: {e}")
        # Fallback to chatbot on error
        return "chatbot"


def create_chatbot():
    """Create and compile the main chatbot orchestrator.
    
    Returns:
        Compiled LangGraph chatbot with subgraphs
    """
    # Create subgraphs
    chatbot_subgraph = create_chatbot_subgraph()
    design_specs_subgraph = create_design_specs_subgraph()
    
    # Store subgraphs for use in routing functions
    def route_to_chatbot(state: ChatState) -> Dict[str, Any]:
        return chatbot_chat(chatbot_subgraph, state["message"], state.get("history", []))
    
    def route_to_design_specs(state: ChatState) -> Dict[str, Any]:
        return process_design_request(design_specs_subgraph, state["message"], state.get("history", []))
    
    # Create the main graph
    graph = StateGraph(ChatState)
    
    # Add subgraph nodes
    graph.add_node("chatbot", route_to_chatbot)
    graph.add_node("design_specs", route_to_design_specs)
    
    # Add conditional routing from START
    graph.add_conditional_edges(
        START,
        classify_and_route,
        {
            "chatbot": "chatbot",
            "design_specs": "design_specs"
        }
    )
    graph.add_edge("chatbot", END)
    graph.add_edge("design_specs", END)
    
    # Compile the graph
    return graph.compile()


def chat_with_bot(
    chatbot, 
    message: str, 
    history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Chat with the bot using subgraphs.
    
    Args:
        chatbot: Compiled chatbot orchestrator
        message: User message
        history: Optional conversation history
        
    Returns:
        Dictionary with bot response and updated history
    """
    if history is None:
        history = []
    
    initial_state = {
        "message": message,
        "history": history,
        "intent": "",
        "response": "",
        "context": {}
    }
    
    result = chatbot.invoke(initial_state)
    return result
