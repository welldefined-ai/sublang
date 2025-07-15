"""Chatbot subgraph with isolated state and functions."""

from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from .nodes.generate_response import generate_response

# Isolated state for chatbot subgraph
class ChatbotState(TypedDict):
    """State structure for the chatbot subgraph."""
    message: str
    history: List[Dict[str, str]]
    intent: str
    response: str
    context: Dict[str, str]


def classify_intent(state: ChatbotState) -> str:
    """Classify intent for routing within chatbot subgraph.
    
    Args:
        state: Current chatbot state
        
    Returns:
        Handler name to route to ("general")
    """
    # For now, chatbot subgraph only handles general responses
    return "general"


def create_chatbot_subgraph():
    """Create and compile the chatbot subgraph.
    
    Returns:
        Compiled LangGraph chatbot subgraph
    """
    # Create the graph
    graph = StateGraph(ChatbotState)
    
    # Add nodes
    graph.add_node("generate_response", generate_response)
    
    # Add edges
    graph.add_edge(START, "generate_response")
    graph.add_edge("generate_response", END)
    
    # Compile the graph
    return graph.compile()


def chat_with_bot(
    chatbot, 
    message: str, 
    history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Chat with the chatbot subgraph.
    
    Args:
        chatbot: Compiled chatbot subgraph
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