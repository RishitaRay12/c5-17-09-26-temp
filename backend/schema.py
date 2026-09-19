import operator
from typing import TypedDict, Literal, Annotated
from pydantic import BaseModel, EmailStr

class AgentState(TypedDict):
    messages: Annotated[list[str], operator.add]
    query: str
    user_role: Literal["employee", "customer"]  # Role segregation
    route: Literal["rag", "sql", "hybrid"]       # Execution route
    rag_context: str
    retrieved_sources: list[dict]
    sql_context: str
    token_usage: dict
    risk_level: Literal["low", "medium", "high"]
    compliance_flags: list[str]
    validation_result: Literal["approved", "qualified", "blocked"]
    relevance_score: float
    faithfulness_score: float
    confidence_score: float
    trace_id: str
    human_handoff: bool
    evaluator_feedback: str
    retry_count: int
    max_retries: int
    final_response: str


class UploadResponse(BaseModel):
    filename: str
    status: str
    files_processed: int = 0
    documents_added: int = 0

class ChatRequest(BaseModel):
    thread_id: str
    question: str

class SourceMetadata(BaseModel):
    source: str          # e.g., "Employee_Handbook.pdf"
    page: int |None
    snippet: str |None

class ChatResponse(BaseModel):
    thread_id: str
    question: str
    answer: str
    sources: list[SourceMetadata] = []
    token_usage: dict | None


class ThreadIdResponse(BaseModel):
    username: str
    thread_id: str

class ThreadItem(BaseModel):
    thread_id: str
    title: str  # First user query
    last_updated: str | None

class UserRegister(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
