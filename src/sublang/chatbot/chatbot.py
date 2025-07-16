"""Main chatbot controller with intent classification and subgraph routing."""

from typing import Dict, List, Optional, Any
import litellm
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from pathlib import Path
from sublang.utils import config, PromptLoader
from sublang.design_specs import create_design_specs_subgraph, process_design_request
from sublang.chatbot.nodes.generate_response import generate_response

# Initialize prompt loader for chatbot subgraph
prompt_loader = PromptLoader(str(Path(__file__).parent / "prompts"))

# Chatbot controller state
class ChatbotState(TypedDict):
    """State structure for the main chatbot controller."""
    message: str
    history: List[Dict[str, str]]
    intent: str
    response: str
    context: Dict[str, str]


def classify_and_route(state: ChatbotState) -> str:
    """Classify intent and route to appropriate handler using LLM.
    
    Args:
        state: Current chatbot state
        
    Returns:
        Handler name to route to ("general" or "design_specs")
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
            return "general"
    
    except Exception as e:
        print(f"Error in LLM classification: {e}")
        # Fallback to general on error
        return "general"


def create_chatbot():
    """Create and compile the main chatbot with subgraph routing.
    
    Returns:
        Compiled LangGraph chatbot
    """
    # Create design specs subgraph
    design_specs_subgraph = create_design_specs_subgraph()
    
    # Create routing function for design specs
    def route_to_design_specs(state: ChatbotState) -> Dict[str, Any]:
        return process_design_request(design_specs_subgraph, state["message"], state.get("history", []))
    
    # Create the main graph
    graph = StateGraph(ChatbotState)
    
    # Add nodes
    graph.add_node("generate_response", generate_response)
    graph.add_node("design_specs", route_to_design_specs)
    
    # Add conditional routing from START
    graph.add_conditional_edges(
        START,
        classify_and_route,
        {
            "general": "generate_response",
            "design_specs": "design_specs"
        }
    )
    graph.add_edge("generate_response", END)
    graph.add_edge("design_specs", END)
    
    # Compile the graph
    return graph.compile()


def chat_with_bot(
    chatbot, 
    message: str, 
    history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Chat with the main chatbot.
    
    Args:
        chatbot: Compiled chatbot
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