import re
from langfuse import observe
from schema import AgentState


_SENSITIVE_DATA_PATTERNS = (
    r"\b(ssn|social security|credit card|bank account|password|api key|secret)\b",
    r"\b(show|give|export|list|download|reveal)\b.{0,40}\b(employee|customer|vendor)\b.{0,40}\b(data|records|details|information)\b",
)
_HIGH_RISK_PATTERNS = (
    r"\b(bypass|disable|circumvent|ignore)\b.{0,40}\b(control|policy|audit|security|approval)\b",
    r"\b(delete|alter|falsify|backdate)\b.{0,40}\b(record|log|audit|review|evidence)\b",
)


def _matches_any(query: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, query, re.IGNORECASE) for pattern in patterns)

@observe()
def compliance_risk_validator_node(state: AgentState):
    """Applies access and operational-risk checks before response generation."""
    query = state["query"]
    role = state["user_role"]
    route = state["route"]
    flags: list[str] = []

    if role == "customer" and route in {"sql", "hybrid"}:
        flags.append("customer_internal_data_access")

    if _matches_any(query, _SENSITIVE_DATA_PATTERNS):
        flags.append("sensitive_personal_or_credential_data")

    if _matches_any(query, _HIGH_RISK_PATTERNS):
        flags.append("control_or_record_tampering_request")

    if any(flag in flags for flag in (
        "sensitive_personal_or_credential_data",
        "control_or_record_tampering_request",
    )):
        risk_level = "high"
        validation_result = "blocked"
    elif flags:
        risk_level = "medium"
        validation_result = "qualified"
    else:
        risk_level = "low"
        validation_result = "approved"

    return {
        "risk_level": risk_level,
        "compliance_flags": flags,
        "validation_result": validation_result,
    }