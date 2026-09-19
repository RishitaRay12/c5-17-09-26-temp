from langgraph.graph import StateGraph, START, END
from schema import AgentState
from app.nodes.classifier import role_classifier_node
from app.nodes.direct_chat import direct_chat_node
from app.nodes.employer import employee_worker_node
from app.nodes.customer import customer_worker_node
from app.nodes.validator import compliance_risk_validator_node
from app.nodes.synthesizer import synthesizer_node
from app.nodes.score_evaluator import score_evaluator_node, route_by_confidence
from app.nodes.human_handoff import human_handoff_node
from langgraph.checkpoint.memory import MemorySaver
import sqlite3
import os
from langgraph.checkpoint.sqlite import SqliteSaver

chat_db_path = os.path.join(os.getcwd(), "chat_memory.sqlite")
chat_conn = sqlite3.connect(chat_db_path, check_same_thread=False)
chat_checkpointer = SqliteSaver(chat_conn)
# agent_app = workflow.compile(checkpointer=chat_checkpointer)
chat_checkpointer.setup() #Ensure SQLite tables exist for checkpoints!


def delete_thread_checkpoints(thread_id: str) -> None:
    """Remove all LangGraph checkpoint data for a thread."""
    with chat_conn:
        tables = {
            row[0]
            for row in chat_conn.execute(
                "SELECT name FROM sqlite_master WHERE type = ?",
                ("table",),
            ).fetchall()
        }
        for table in ("checkpoint_writes", "checkpoint_blobs", "checkpoints"):
            if table not in tables:
                continue
            chat_conn.execute(
                f"DELETE FROM {table} WHERE thread_id = ?",
                (thread_id,),
            )


# config = None

def route_by_role(state: AgentState) -> str:
    role = None
    if state["route"] == "direct":
        role = "direct"
    elif state["user_role"] == "employee":
        role = "employee_worker" 
    elif state["user_role"] == "customer":
        role = "customer_worker"

    return role

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("classifier", role_classifier_node)
workflow.add_node("direct", direct_chat_node)
workflow.add_node("employee_worker", employee_worker_node)
workflow.add_node("customer_worker", customer_worker_node)
workflow.add_node("compliance_risk_validator", compliance_risk_validator_node)
workflow.add_node("synthesizer", synthesizer_node)
workflow.add_node("score_evaluator", score_evaluator_node)
workflow.add_node("human_handoff", human_handoff_node)
# Add Edges
workflow.add_edge(START, "classifier")

# Dynamic fan-out based on assigned user role
workflow.add_conditional_edges(
    "classifier",
    route_by_role,
    {
        "direct": "direct",
        "employee_worker": "employee_worker",
        "customer_worker": "customer_worker"
    }
)

workflow.add_edge("employee_worker", "compliance_risk_validator")
workflow.add_edge("customer_worker", "compliance_risk_validator")
workflow.add_edge("compliance_risk_validator", "synthesizer")
workflow.add_edge("synthesizer", "score_evaluator")

workflow.add_conditional_edges(
    "score_evaluator",
    route_by_confidence,
    {
        "pass": END,
        "refine": "synthesizer",       # Synthesizer reads state["evaluator_feedback"] to refine
        "escalate": "human_handoff"    # Halts execution for human review
    }
)

workflow.add_edge("human_handoff", END)
# workflow.add_edge("synthesizer", END)

app = workflow.compile(checkpointer=chat_checkpointer)