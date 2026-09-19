from schema import AgentState
from llm import get_llm
from langchain_core.messages import AIMessage
from langfuse import observe

@observe()
def synthesizer_node(state: AgentState):
    """Formulates the final response using role-tailored prompt constraints."""
    query = state["query"]
    role = state["user_role"]
    validation_result = state.get("validation_result", "approved")
    risk_level = state.get("risk_level", "low")
    compliance_flags = state.get("compliance_flags", [])
    rag_ctx = state.get("rag_context", "N/A")
    sql_ctx = state.get("sql_context", "N/A")
    current_retries = state.get("retry_count", 0)
    if validation_result == "blocked":
        return {
            "final_response": (
                "I can't help with that request because it involves sensitive data "
                "or bypassing a compliance or security control."
            )
        }
    
    if role == "employee":
        instructions = (
            "You are an Internal Compliance & Decision Support Assistant for EMPLOYEES. "
            "Provide procedural steps, cite specific policy clauses, highlight audit flags, "
            "and list explicit manager action items where applicable."
        )
    else:
        instructions = (
            "You are a Customer Service Assistant for RETAIL CUSTOMERS. "
            "Deliver a friendly, simple, empathetic response focused purely on public policy rules. "
            "Do NOT reference internal systems, SQL databases, or internal compliance jargon."
        )

    prompt = f"""
    You are a retail customer service assistant.. for simple queries call llm directly
    {instructions}

    Compliance validation: {validation_result}
    Risk level: {risk_level}
    Compliance flags: {", ".join(compliance_flags) or "none"}
    Follow the validation outcome. For a qualified request, provide only the
    permitted public or policy-level information and do not infer restricted details.

    User Query: {query}

    --- PDF Policy Document Context (RAG) ---
    {rag_ctx}

    --- Database Context (SQL) ---
    {sql_ctx}
    """
    response = get_llm().invoke(prompt)
    response_text = response.content
    usage = (response.response_metadata or {}).get("token_usage") or {}
    cached_tokens = (
        (usage.get("prompt_tokens_details") or {})
                .get("cached_tokens", 0)
    )
    token_info = {
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                        "prompt_tokens_details": {
                            "cached_tokens": cached_tokens
                        }
                    },
    
                    "cache_status": "HIT" if cached_tokens > 0 else "MISS"
                }
    return {"final_response": response_text,
            "messages": [AIMessage(content=response_text)],
            "retry_count": current_retries + 1,
            "token_usage": token_info
            }