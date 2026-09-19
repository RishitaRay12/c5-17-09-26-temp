from schema import AgentState
from rag import execute_rag_retrieval, execute_sql_query
from langfuse import observe

@observe()
def employee_worker_node(state: AgentState):
    """
    Handles queries for internal staff with full authorization.
    Executes RAG, SQL, or Hybrid pathways and passes compliance-level context.
    """
    query = state["query"]
    route = state["route"]
    
    rag_context = "N/A"
    retrieved_sources = []
    sql_context = "N/A"
    
    if route in ["rag", "hybrid"]:
        rag_context, retrieved_sources = execute_rag_retrieval(query)
        
    if route in ["sql", "hybrid"]:
        sql_context = execute_sql_query(query)
        
    return {
        "rag_context": rag_context,
        "retrieved_sources": retrieved_sources,
        "sql_context": sql_context
    }