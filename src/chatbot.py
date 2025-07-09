"""Chatbot graph creation and interaction functions."""

from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, START, END
from .state import ChatState
from .nodes import classify_intent, generate_response, design_specs


def route_to_handler(state: ChatState) -> str:
    """Route to appropriate handler based on intent.
    
    Args:
        state: Current chat state
        
    Returns:
        Handler name to route to
    """
    intent = state.get("intent", "GENERAL")
    if intent == "DESIGN_SPECS":
        return "design"
    else:
        return "general"


def create_chatbot():
    """Create and compile the chatbot graph.
    
    Returns:
        Compiled LangGraph chatbot
    """
    # Create the graph
    graph = StateGraph(ChatState)
    
    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("generate_response", generate_response)
    graph.add_node("design_specs", design_specs)
    
    # Add edges with conditional routing
    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        route_to_handler,
        {
            "general": "generate_response",
            "design": "design_specs"
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
    """Chat with the bot using a message.
    
    Args:
        chatbot: Compiled chatbot graph
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
