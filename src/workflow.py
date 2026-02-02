from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import node_listener, node_clerk, node_drafter, node_notifier, node_approver

def create_workflow():
    # 1. Initialize Graph
    workflow = StateGraph(AgentState)

    # 2. Add Nodes
    workflow.add_node("listener", node_listener)
    workflow.add_node("clerk", node_clerk)
    workflow.add_node("drafter", node_drafter)
    workflow.add_node("approver", node_approver)
    workflow.add_node("notifier", node_notifier)

    # 3. Add Edges (Linear Flow)
    workflow.set_entry_point("listener")
    
    # Conditional logic example could go here, but for now we keep it linear
    # Listener -> Clerk -> Drafter -> Approver -> END
    
    # Simple Linear Edges
    workflow.add_edge("listener", "clerk")
    workflow.add_edge("clerk", "drafter")
    workflow.add_edge("drafter", "approver")
    workflow.add_edge("approver", END)

    # 4. Compile
    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app

# Expose the compiled graph
graph_app = create_workflow()
