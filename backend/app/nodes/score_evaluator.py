from pydantic import BaseModel, Field
from schema import AgentState
from llm import get_llm
from langfuse import observe
from app.tools import evaluate_query_for_human_handoff_internal

class QualityEvaluationSchema(BaseModel):
    faithfulness_score: float = Field(
        description="Score between 0.0 and 1.0 indicating if all facts in the response are grounded in the retrieved context."
    )
    relevance_score: float = Field(
        description="Score between 0.0 and 1.0 indicating how directly the response addresses the user query."
    )
    reasoning: str = Field(
        description="Brief explanation highlighting missing facts, ungrounded claims, or missing policy citations."
    )

@observe()
def score_evaluator_node(state: AgentState):
    """LLM-as-a-Judge node to calculate Relevance, Faithfulness, and Confidence."""
    # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_evaluator = get_llm().with_structured_output(QualityEvaluationSchema)

    query = state.get("query", "")
    context_sql = state.get("sql_context", "")
    context_rag = state.get("rag_context", "")
    draft = state.get("final_response", "")

    eval_prompt = f"""
    You are a strict compliance quality auditor. Evaluate the following draft response against the query and retrieved policy context:

    User Query: {query}
    Retrieved Context: {context_sql} and {context_rag}
    Draft Response: {draft}

    Evaluate:
    1. Faithfulness (Grounding): Are claims strictly derived from context?
    2. Relevance: Does it directly answer the query without fluff?
    """

    # Call Structured LLM Evaluator
    eval_result: QualityEvaluationSchema = structured_evaluator.invoke(eval_prompt)

    # 4. Calculate Weighted Confidence Score
    # Faithfulness is weighted higher (60%) for compliance accuracy
    w_faithfulness = 0.60
    w_relevance = 0.40

    composite_confidence = (eval_result.faithfulness_score * w_faithfulness) + \
                           (eval_result.relevance_score * w_relevance)
    # state["confidence_score"] = composite_confidence
    # state["relevance_score"] = round(eval_result.relevance_score, 2)
    # state["faithfulness_score"] = round(eval_result.faithfulness_score, 2)
    # state["evaluator_feedback"] = eval_result.reasoning
    result = evaluate_query_for_human_handoff_internal(state["query"])
    human_handoff_triggered = result["needs_human_escalation"]
    return {
        "faithfulness_score": round(eval_result.faithfulness_score, 2),
        "relevance_score": round(eval_result.relevance_score, 2),
        "confidence_score": round(composite_confidence, 2),
        "evaluator_feedback": eval_result.reasoning,
        "human_handoff": human_handoff_triggered,
        # "final_response": result["detected_keywords_or_concepts"]
    }

def route_by_confidence(state: AgentState):
    CONFIDENCE_THRESHOLD = 0.85
    if state.get("human_handoff", False):
        return "escalate"

    # Pass if composite confidence meets threshold
    if state.get("confidence_score", 0.0) >= CONFIDENCE_THRESHOLD:
        return "pass"

    # Refine if score is below threshold but retries remain
    if state.get("retry_count", 0) < state.get("max_retries", 2):
        return "refine"

    # Escalate to human handoff if retries are exhausted
    return "escalate"