import smtplib
import datetime
import secrets
import os
from typing import Optional, Any, Dict
import logging
from email.mime.text import MIMEText
from schema import AgentState
from langfuse import observe

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("APPLICATION_EMAIL")
EMAIL_TO = os.getenv("SUPPORT_EMAIL")


def generate_handoff_reference_id(now: Optional[datetime.datetime] = None) -> str:
    """Generate a unique handoff reference ID."""
    now = now or datetime.datetime.now(datetime.UTC)
    return f"HO-{now.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(3).upper()}"

def send_handoff_email(context: Dict[str, Any]):
    """Send CLEAN, Sprint Master–aligned human handoff email."""
    if not all([SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO]):
        logger.warning(f"Email settings missing. SMTP_HOST={SMTP_HOST}, SMTP_USERNAME={SMTP_USERNAME}, EMAIL_FROM={EMAIL_FROM}, EMAIL_TO={EMAIL_TO}")
        return
    
    subject = f"[HUMAN HANDOFF] Ref {context['reference_id']}"

    body = f"""
A human handoff has been triggered.

Reference ID: {context['reference_id']}

Timestamp: {context['timestamp_utc']}

Reason for Handoff:
{context['trigger_reason']}

------------------------------------------------------------
Generated Answer:
------------------------------------------------------------
{context['generated_answer']}

------------------------------------------------------------
Evaluation Scores:
------------------------------------------------------------
Faithfulness: {context['evaluation_scores']['faithfulness']}
Relevance: {context['evaluation_scores']['relevance']}
LLM Confidence: {context['evaluation_scores']['confidence']}

"""

    msg = MIMEText(body)
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    try:
        logger.info(f"Attempting to send email from {EMAIL_FROM} to {EMAIL_TO} via {SMTP_HOST}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logger.info("Human handoff email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
    except Exception as e:
        logger.error(f"Failed to send handoff email: {e}")

@observe()
def human_handoff_node(state: AgentState):
    reference_id = generate_handoff_reference_id()
    timestamp_utc = datetime.datetime.now(datetime.UTC).isoformat()
    handoff_context = {
                "reference_id": reference_id,
                # "trace_id": state["trace_id"],
                "timestamp_utc": timestamp_utc,
                # "session_id": session_id,
                # "priority": priority,
                "trigger_reason": state["evaluator_feedback"],

                "query_history": [
                    {"role": "user", "message": state["query"]}
                ],

                "generated_answer": state["final_response"],

                "evaluation_scores": {
                    "faithfulness": state["faithfulness_score"],
                    "relevance": state["relevance_score"],
                    "confidence": state["confidence_score"]
                },

            #     "retrieved_chunks": full_chunks,

            #     "user_metadata": {
            #         "email": request.user_email
            #     },

            #     "conversation_flow": conversation_flow
            }
    
    # Send the handoff email
    send_handoff_email(handoff_context)
    
    return {
        "final_response": f"Escalated to human team with reference ID: {reference_id}"
    }