from schema import AgentState
from rag import execute_rag_retrieval
from langfuse import observe

@observe()
def customer_worker_node(state: AgentState):
    """
    Handles queries for public consumers.
    Executes RAG for public policies, but restricts access to internal SQL tables.
    """
    query = state["query"]
    route = state["route"]
    
    rag_context = "N/A"
    retrieved_sources = []
    sql_context = "Access Restricted: Customers do not have permission to access internal database records."
    
    # Customers execute RAG search for public policy documents
    if route in ["rag", "hybrid"]:
        rag_context, retrieved_sources = execute_rag_retrieval(query)
        
    return {
        "rag_context": rag_context,
        "retrieved_sources": retrieved_sources,
        "sql_context": sql_context
    }
