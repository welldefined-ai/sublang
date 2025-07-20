"""Design specifications subgraph with isolated state and functions."""

from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from .nodes.extract_terms import extract_terms
from .nodes.add_features import add_features
from .nodes.add_constraints import add_constraints
from sublang.utils.model_config import get_langfuse_config

# Isolated state for design_specs subgraph
class DesignSpecsState(TypedDict):
    """State structure for the design_specs subgraph."""
    message: str
    history: List[Dict[str, str]]
    intent: str
    response: str
    context: Dict[str, str]
    terms: str
    features: str


def create():
    """Create and compile the design_specs subgraph.
    
    Returns:
        Compiled LangGraph design_specs subgraph
    """
    # Create the graph
    graph = StateGraph(DesignSpecsState)
    
    # Add nodes
    graph.add_node("extract_terms", extract_terms)
    graph.add_node("add_features", add_features)
    graph.add_node("add_constraints", add_constraints)
    
    # Add edges
    graph.add_edge(START, "extract_terms")
    graph.add_edge("extract_terms", "add_features")
    graph.add_edge("add_features", "add_constraints")
    graph.add_edge("add_constraints", END)
    
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
        "context": {},
        "terms": "",
        "features": ""
    }
    
    # Get LangFuse config for tracing
    langfuse_config = get_langfuse_config()
    result = design_graph.invoke(initial_state, config=langfuse_config)
    return result
