"""Design specifications subgraph with isolated state and functions."""

from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from .nodes.design_specs import design_specs

# Isolated state for design_specs subgraph
class DesignSpecsState(TypedDict):
    """State structure for the design_specs subgraph."""
    message: str
    history: List[Dict[str, str]]
    intent: str
    response: str
    context: Dict[str, str]


def create():
    """Create and compile the design_specs subgraph.
    
    Returns:
        Compiled LangGraph design_specs subgraph
    """
    # Create the graph
    graph = StateGraph(DesignSpecsState)
    
    # Add nodes
    graph.add_node("design_specs", design_specs)
    
    # Add edges
    graph.add_edge(START, "design_specs")
    graph.add_edge("design_specs", END)
    
    # Compile the graph
    return graph.compile()


def process(
    design_graph, 
    message: str, 
    history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Process request with the design_specs subgraph.
    
    Args:
        design_graph: Compiled design_specs subgraph
        message: User message
        history: Optional conversation history
        
    Returns:
        Dictionary with design response and updated history
    """
    if history is None:
        history = []
    
    initial_state = {
        "message": message,
        "history": history,
        "intent": "DESIGN_SPECS",
        "response": "",
        "context": {}
    }
    
    result = design_graph.invoke(initial_state)
    return result