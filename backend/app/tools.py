# import os
# from typing import List
# from pydantic import BaseModel, Field
# from langchain_openai import ChatOpenAI
# # from mcp.server.fastmcp import FastMCP

# # mcp = FastMCP("llm-compliance-classifier")
# # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# model = os.getenv("LLM_MODEL")
# api_key = os.getenv("LLM_KEY")
# url = os.getenv("BASIC_URL")
# client = ChatOpenAI(model=model, api_key=api_key, base_url=url)
# # Define structured output model
# class EscalationAnalysis(BaseModel):
#     contains_target_risks: bool = Field(
#         description="True if the query matches any target high-risk scenarios."
#     )
#     detected_keywords_or_concepts: List[str] = Field(
#         description="Extracted risk topics (e.g., 'legal hold', 'restricted jurisdiction')."
#     )
#     risk_level: str = Field(
#         description="Assigned risk level: CRITICAL, HIGH, MEDIUM, or LOW."
#     )
#     needs_human_escalation: bool = Field(
#         description="True if human review by compliance or legal team is required."
#     )
#     reasoning: str = Field(
#         description="Brief explanation of why escalation is or is not required."
#     )

# # @mcp.tool()
# def analyze_compliance_query_with_llm(query_text: str) -> dict:
#     """
#     Uses an LLM to evaluate if a user query contains restricted policy concepts 
#     (legal holds, cross-border transfers, unverified closures, etc.) and determines human escalation.
#     """
#     system_prompt = (
#         "You are an enterprise legal and compliance risk evaluator. "
#         "Analyze the user query to detect any of the following restricted risk categories:\n"
#         "- Cross-border data transfer involving restricted jurisdictions\n"
#         "- Deletion requests under active legal hold\n"
#         "- Approval overrides for Critical-risk vendors\n"
#         "- Hospitality or gift approvals involving overseas suppliers\n"
#         "- Audit findings overdue beyond resolution targets\n"
#         "- Conflicting policy clauses across departments\n"
#         "- Vendor onboarding with unresolved compliance findings\n"
#         "- High-severity issues closed without resolution evidence\n\n"
#         "Evaluate the semantic meaning, even if exact keywords are paraphrased.\n"
#         "If the query matches ANY of these risk categories, set needs_human_escalation to true. "
#         "Otherwise, set it to false."
#     )

#     structured_llm = client.with_structured_output(EscalationAnalysis)

# # 3. Invoke the structured model
#     analysis: EscalationAnalysis = structured_llm.invoke([
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": f"Query to evaluate:\n{query_text}"}
#     ])

#     # Extract parsed Pydantic output
#     # analysis: EscalationAnalysis = response.choices[0].message.parsed
#     return analysis.model_dump()

# # if __name__ == "__main__":
# #     mcp.run(transport="stdio")
import os
from typing import List, Dict, Any
import pandas as pd
from datasets import load_dataset
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from llm import get_llm

# Initialize FastMCP Server
mcp = FastMCP("fed-legal-handoff-evaluator")

# Helper to extract user prompts from dataset messages
def extract_prompt(messages):
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") == "user":
            return msg.get("content", "")
    return ""

# Lazy load helpers
_df = None
_vectorizer = None
_tfidf_matrix = None

def _get_dataset_and_matrix():
    global _df, _vectorizer, _tfidf_matrix
    if _df is not None:
        return _df, _vectorizer, _tfidf_matrix
    
    hf_token = os.getenv("HF_TOKEN")
    try:
        dataset = load_dataset("flwrlabs/fed-legal", split="train", token=hf_token)
        _df = pd.DataFrame(dataset)
    except Exception:
        _df = pd.DataFrame(columns=["messages", "client_id", "task_type", "example_id"])
        
    if not _df.empty:
        _df["prompt_text"] = _df["messages"].apply(extract_prompt)
        _vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        _tfidf_matrix = _vectorizer.fit_transform(_df["prompt_text"].fillna(""))
    else:
        _vectorizer = None
        _tfidf_matrix = None
        
    return _df, _vectorizer, _tfidf_matrix

# 2. Define Pydantic Schema for LLM Output
class HandoffDecision(BaseModel):
    contains_restricted_scenarios: bool = Field(
        description="True if query involves legal holds, cross-border restrictions, overrides, or unverified closures."
    )
    risk_level: str = Field(
        description="Assigned risk level: CRITICAL, HIGH, MEDIUM, or LOW."
    )
    needs_human_escalation: bool = Field(
        description="True if the request must be handed off to a human compliance/legal officer."
    )
    flagged_concepts: List[str] = Field(
        description="Extracted compliance topics (e.g., 'legal hold', 'restricted jurisdiction')."
    )
    reasoning: str = Field(
        description="Detailed explanation justifying whether human handoff is required."
    )

# 3. Initialize ChatOpenAI with Structured Output

client = get_llm()

structured_llm = client.with_structured_output(HandoffDecision)


# ---------------------------------------------------------
# MCP Tool: Evaluate Query Using Dataset Context
# ---------------------------------------------------------
def evaluate_query_for_human_handoff_internal(query_text: str) -> Dict[str, Any]:
    """
    Retrieves similar provisions from the flwrlabs/fed-legal dataset and evaluates
    if the incoming query contains compliance risks that require human handoff.
    """
    # Step A: Retrieve similar legal examples from the dataset
    retrieved_context = ""
    df_data, vec, matrix = _get_dataset_and_matrix()
    if df_data is not None and not df_data.empty:
        query_vec = vec.transform([query_text])
        sims = cosine_similarity(query_vec, matrix).flatten()
        top_indices = sims.argsort()[-2:][::-1]
        
        examples = []
        for idx in top_indices:
            row = df_data.iloc[idx]
            examples.append(f"- Silo {row['client_id']} ({row['task_type']}): {row['prompt_text'][:200]}...")
        retrieved_context = "\n".join(examples)

    # Step B: Evaluate query with ChatOpenAI
    
    system_prompt = (
        "You are an enterprise compliance auditor. Analyze the query to decide if it requires human escalation.\n"
        "Human escalation IS REQUIRED (needs_human_escalation = true) if any of these apply:\n"
        "- Deletion requests under an active legal hold\n"
        "- Cross-border data transfers to restricted jurisdictions\n"
        "- Approval overrides for Critical-risk vendors\n"
        "- Hospitality or gift approvals involving overseas suppliers\n"
        "- Overdue audit findings beyond target resolution dates\n"
        "- Vendor onboarding with unresolved compliance findings\n"
        "- Closing High-severity / Critical issues without resolution evidence\n"
    )

    user_input = (
        f"Dataset Precedent Context:\n{retrieved_context}\n\n"
        f"Incoming User Query:\n{query_text}"
    )

    analysis: HandoffDecision = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ])

    return analysis.model_dump()


@mcp.tool()
def evaluate_query_for_human_handoff(query_text: str) -> Dict[str, Any]:
    """
    Retrieves similar provisions from the flwrlabs/fed-legal dataset and evaluates
    if the incoming query contains compliance risks that require human handoff.
    """
    return evaluate_query_for_human_handoff_internal(query_text)



# if __name__ == "__main__":
#     mcp.run(transport="stdio")