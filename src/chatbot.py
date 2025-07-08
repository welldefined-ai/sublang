"""Chatbot graph creation and interaction functions."""

from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, START, END
from .state import ChatState
from .nodes import classify_intent, generate_response


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
    
    # Add edges
    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "generate_response")
    graph.add_edge("generate_response", END)
    
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
