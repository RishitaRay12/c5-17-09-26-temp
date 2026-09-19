import json
from schema import AgentState
from llm import get_llm
from langfuse import observe

@observe()
def role_classifier_node(state: AgentState):
    """Classifies user role and operational execution route."""
    query = state["query"]
    
    prompt = f"""
    Analyze the following retail query and classify two parameters:

    1. user_role ('employee' vs 'customer'):
       - 'employee': Mentions vendor compliance, audit logs, data retention, ISO rules, internal guidelines, or IT security policies.
       - 'customer': Mentions consumer return policies, warranties, store hours, order status, public privacy policies.

    2. route ('rag' vs 'sql' vs 'hybrid'):
       - 'direct': Simple chitchat, greetings, identity questions (e.g., 'what is your name?'), or casual conversation that DOES NOT require document/database lookup.
       - 'rag': Unstructured policy search.
       - 'sql': Database lookup across tables (vendors, audit_logs, retention_records, compliance_reviews).
       - 'hybrid': Requires both document search AND database lookup.

    Query: "{query}"

    Respond ONLY in valid JSON:
    {{"user_role": "employee" | "customer", "route": "direct" | "rag" | "sql" | "hybrid"}}
    """
    
    res = get_llm().invoke(prompt).content.strip()
    parsed = json.loads(res)
    if res.startswith("```"):
        res = res.split("```")[1].replace("json", "").strip()

    parsed = json.loads(res)
    route = parsed.get("route", "rag")
    
    updates = {
        "user_role": parsed.get("user_role", "customer"),
        "route": route,
        "human_handoff": False
    }
    if route == "direct":
        updates["relevance_score"] = 1.0
        updates["faithfulness_score"] = 1.0
        updates["confidence_score"] = 1.0
    return updates
