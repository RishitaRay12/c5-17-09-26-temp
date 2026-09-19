import logging
import uuid
from datetime import datetime
from fastapi import HTTPException, FastAPI, UploadFile, File, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from app.chunking import _process_uploaded_files
from app.graph import app as agent_app, chat_checkpointer, delete_thread_checkpoints
from app.routes.users import router as user_router
from app.user import (
    delete_chat_thread,
    get_chat_history,
    get_chat_thread_ids,
    get_current_user,
    save_chat_message,
)
from schema import SourceMetadata, UploadResponse, ChatRequest, ChatResponse, ThreadIdResponse, ThreadItem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="PDF Vector Store API",
    description="Extracts content & tables from uploaded files and stores embeddings in ChromaDB",
    tags=["Chatbot and File Upload"],
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

langfuse_client = get_client()
app.include_router(user_router)  # Include user routes for registration and login


# async def _coerce_upload_files(
#     files: list[UploadFile] | None = File(default=None),
#     single_file: UploadFile | None = File(default=None),
# ) -> list[UploadFile]:
#     resolved_files = list(files or [])
#     if single_file is not None:
#         resolved_files.append(single_file)

#     if not resolved_files:
#         raise HTTPException(status_code=400, detail="No files were uploaded.")

#     return resolved_files


# @app.post("/upload-document", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
# async def upload_and_index_document(
#     files: list[UploadFile] | None = File(default=None),
#     single_file: UploadFile | None = File(default=None),
#     current_user: dict = Depends(get_current_user),
# ):
#     resolved_files = await _coerce_upload_files(files, single_file)
#     results = await _process_uploaded_files(resolved_files)
#     total_documents = sum(result.documents_added for result in results)
#     aggregate_filename = "multiple_files" if len(results) > 1 else results[0].filename
#     return UploadResponse(
#         filename=aggregate_filename,
#         status="success",
#         files_processed=len(results),
#         documents_added=total_documents,
#     )


# @app.post("/upload-directory", response_model=list[UploadResponse], status_code=status.HTTP_201_CREATED)
# async def upload_and_index_directory(
#     files: list[UploadFile] | None = File(default=None),
#     single_file: UploadFile | None = File(default=None),
#     current_user: dict = Depends(get_current_user),
# ):
#     resolved_files = await _coerce_upload_files(files, single_file)
#     return await _process_uploaded_files(resolved_files)


async def _coerce_upload_files(
    single_file: UploadFile = File(...),
) -> list[UploadFile]:
    if not single_file:
        raise HTTPException(status_code=400, detail="No files were uploaded.")
    return [single_file]


@app.post("/upload-document", tags=["File Upload"], response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_index_document(
    single_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    resolved_files = await _coerce_upload_files(single_file)
    results = await _process_uploaded_files(resolved_files)
    total_documents = sum(result.documents_added for result in results)
    aggregate_filename = "multiple_files" if len(results) > 1 else results[0].filename
    return UploadResponse(
        filename=aggregate_filename,
        status="success",
        files_processed=len(results),
        documents_added=total_documents,
    )


# @app.post("/upload-directory", response_model=list[UploadResponse], status_code=status.HTTP_201_CREATED)
# async def upload_and_index_directory(
#     single_file: UploadFile = File(...),
#     current_user: dict = Depends(get_current_user),
# ):
#     resolved_files = await _coerce_upload_files(single_file)
#     return await _process_uploaded_files(resolved_files)

# chat_checkpointer.put(config=config)
@app.post("/create_threads", tags=["New Threads"], response_model=ThreadIdResponse, status_code=status.HTTP_201_CREATED)
def create_thread_id(current_user: dict = Depends(get_current_user)):
    return ThreadIdResponse(thread_id=str(uuid.uuid4()), username=current_user.get("username", "anonymous"))


@app.delete("/threads/{thread_id}", tags=["Delete Threads"], response_model=dict)
def delete_thread(thread_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a user's chat messages and graph checkpoints for one thread."""
    username = current_user.get("username", "anonymous")
    deleted_messages = delete_chat_thread(username=username, thread_id=thread_id)
    if deleted_messages == 0:
        raise HTTPException(status_code=404, detail="Thread not found")

    delete_thread_checkpoints(thread_id)
    return {
        "thread_id": thread_id,
        "deleted_messages": deleted_messages,
        "deleted": True,
    }


# @app.get("/threads/{thread_id}", response_model=dict)
# def get_thread_state(thread_id: str):
#     config = {"configurable": {"thread_id": thread_id}}
#     state = agent_app.get_state(config)
#     return {
#         "thread_id": thread_id,
#         "values": state.values if state else {},
#         "metadata": state.metadata if state else {},
#     }


@app.post("/chat", tags=["Chatbot"], response_model=ChatResponse)
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    thread_id = request.thread_id.strip()
    if not thread_id:
        raise HTTPException(status_code=400, detail="thread_id is required")
    langfuse_handler = CallbackHandler()
    try:
        config = {
            "callbacks": [
                langfuse_handler,
            ],
            "metadata": {
                "user_id": current_user.get("username", "anonymous"),
                "langfuse_session_id": thread_id,
            },
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": "",
            }
        }

        initial_state = {
            "messages": [HumanMessage(content=request.question)],
            "query": request.question,
            "retrieved_sources": [],
            "human_handoff": False,
            "token_usage": {},
            "retry_count": 0,
            "max_retries": 2,
        }

        save_chat_message(
            username=current_user.get("username", "anonymous"),
            thread_id=thread_id,
            role="user",
            message=request.question,
        )
        
        with langfuse_client.start_as_current_observation(
            as_type="span",
            name="startup-evaluation",
        ) as evaluation_span:
            result = agent_app.invoke(initial_state, config=config)
            answer = result.get("final_response", "")
            tokens_used = result.get("token_usage", {})
            processed_sources = []
            for source in result.get("retrieved_sources") or []:
                source = source or {}
                processed_sources.append(
                    SourceMetadata(
                        source=source.get("source", "Unknown Source"),
                        page=source.get("page"),
                        snippet=source.get("snippet"),
                    )
                )
            # usage = result.get("response_metadata", {}).get("token_usage", {})
            # cached_tokens = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
            save_chat_message(
            username=current_user.get("username", "anonymous"),
            thread_id=thread_id,
            role="assistant",
            message=answer,
            sources=[source.model_dump() for source in processed_sources],
            token_usage=tokens_used,
        )
            score_values = {
                "relevance_score": result.get("relevance_score"),
                "faithfulness_score": result.get("faithfulness_score"),
                "confidence_score": result.get("confidence_score"),
            }
            for score_name, score_value in score_values.items():
                if isinstance(score_value, (int, float)):
                    langfuse_client.score_current_trace(
                        name=score_name,
                        value=float(score_value),
                        data_type="NUMERIC",
                    )
            evaluation_span.update(
                metadata={
                    **score_values,
                    "thread_id": thread_id
                }
            )
            return ChatResponse(
                thread_id=thread_id,
                question=request.question,
                answer=answer,
                sources=processed_sources,
                token_usage=tokens_used
            )
    except Exception as exc:
        logger.exception("Chatbot failed: thread_id=%s", thread_id)
        raise HTTPException(status_code=500, detail=str(exc))

# @app.get("/threads", response_model=List[ThreadItem])
# def list_threads(current_user: dict = Depends(get_current_user)):
#     """
#     Fetches stored thread snapshots, extracts the first human query
#     to display in the list/UI selection menu.
#     """
#     threads_summary = []
#     query_filter = {"user_id": current_user.get("username", "anonymous")}
#     # List distinct thread IDs managed by checkpointer
#     # For SqliteSaver or MemorySaver, checkpointer.list(config=None) retrieves checkpoints
#     # checkpoints = list(chat_checkpointer.list(config=None))
#     # Pass a config dictionary with a metadata filter
#     # checkpoints = list(chat_checkpointer.list(config={"metadata": {"user_id": current_user.get("username", "anonymous")}}))

    
#     # Group checkpoints by thread_id to identify first messages
#     threads_map = {}
#     for checkpoint_tuple in chat_checkpointer.list(config=None, filter=query_filter):
#         configs = checkpoint_tuple.config
#         thread_id = configs["configurable"]["thread_id"]
#         if thread_id not in threads_map:
#             threads_map[thread_id] = checkpoint_tuple
#     # for cp in checkpoints:
#     #     tid = cp.config["configurable"]["thread_id"]
#         # if tid not in threads_map:
#         #     threads_map[tid] = cp.checkpoint
#     threads_summary = []
    
#     for thread_id, checkpoint_tuple in threads_map.items():
#         checkpoint_data = checkpoint_tuple.checkpoint
#         channel_values = checkpoint_data.get("channel_values", {})
#     # for tid, checkpoint in threads_map.items():
#     #     # Get channel values saved in the graph state
#     #     channel_values = checkpoint.get("channel_values", {})
#     #     messages = channel_values.get("messages", [])
        
#         # Locate the first human query to set as thread title
#         messages = channel_values.get("messages", [])
        
#         # Safely extract any extra metadata you might have saved
#         metadata = checkpoint_tuple.metadata or {}
        
#         # formatted_histories.append({
#         #     "thread_id": thread_id,
#         #     "updated_at": checkpoint_data.get("ts"), # Timestamp of last message/turn
#         #     "metadata": metadata,
#         #     "messages": messages  # The actual list of BaseMessage objects
#         # })
#         first_query = None
#         for msg in messages:
#             if isinstance(msg, HumanMessage) or getattr(msg, "type", "") == "human":
#                 first_query = msg.content
#                 break
#             elif isinstance(msg, dict) and msg.get("type") in ("human", "user"):
#                 first_query = msg.get("content")
#                 break
#         if not first_query:
#             first_query = channel_values.get("query", "Empty Chat")
#         first_query_str = str(first_query)
#         title = first_query_str if len(first_query) <= 50 else f"{first_query[:47]}..."
#         threads_summary.append(
#             ThreadItem(
#                 thread_id=thread_id,
#                 title=title
#             )
#         )
        
#     return threads_summary

# @app.get("/threads/{thread_id}/history")
# def get_thread_history(thread_id: str):
#     """Fetches full chat history for a specific thread_id."""
#     config = {"configurable": {"thread_id": thread_id}}
#     state = agent_app.get_state(config)
    
#     if not state or not state.values:
#         raise HTTPException(status_code=404, detail="Thread not found")
        
#     messages = state.values.get("messages", [])
#     history = []

#     for m in messages:
#         # Handle dict format (de-serialized checkpoints)
#         if isinstance(m, dict):
#             msg_type = m.get("type", "")
#             role = "user" if msg_type in ("human", "user") else "assistant"
#             content = m.get("content", "")
#         # Handle LangChain Message objects
#         else:
#             msg_type = getattr(m, "type", "")
#             if isinstance(m, HumanMessage) or msg_type in ("human", "user"):
#                 role = "user"
#             else:
#                 role = "assistant"
#             content = getattr(m, "content", "")

#         history.append({"role": role, "content": content})

#     return history

# # def main():
# #     query = input("whats your query?")
# #     input_state = {
# #         "query": query,
# #         "human_handoff": False,
# #         "retry_count": 0,
# #         "max_retries": 2,
# #     }
# #     result = agent_app.invoke(input_state, config={"configurable": {"thread_id": "demo-thread"}})
# #     print("Role Detected:", result["user_role"])
# #     print("Execution Route:", result["route"])
# #     print("Risk Level:", result["risk_level"])
# #     print("Validation:", result["validation_result"])
# #     if result["compliance_flags"]:
# #         print("Compliance Flags:", ", ".join(result["compliance_flags"]))
# #     print("Final Response:\n", result["final_response"])


# # if __name__ == '__main__':
# #     main()

@app.get("/threads", response_model=list[ThreadItem], tags=["List Threads"])
def list_threads(current_user: dict = Depends(get_current_user)):
    """
    Fetches stored thread snapshots, extracts the first human query
    to display in the list/UI selection menu.
    """
    user_id = current_user.get("username", "anonymous")
    owned_thread_ids = get_chat_thread_ids(user_id)
    threads_map = {}

    # Query checkpoints using metadata filter in config
    # config_filter = {"configurable": {"checkpoint_ns": ""}, "metadata": {"user_id": user_id}}
    
    # Iterate through saved state checkpoints
    for checkpoint_tuple in chat_checkpointer.list(config=None):
        cp_config = checkpoint_tuple.config or {}
        cp_metadata = checkpoint_tuple.metadata or {}

        
        # Only expose threads that have application messages owned by this user.
        if thread_id := cp_config.get("configurable", {}).get("thread_id"):
            if thread_id not in owned_thread_ids:
                continue
        else:
            continue

        # Group by thread_id to keep the latest state snapshot
        if thread_id and thread_id not in threads_map:
            threads_map[thread_id] = checkpoint_tuple

    threads_summary = []
    
    for thread_id, checkpoint_tuple in threads_map.items():
        checkpoint_data = checkpoint_tuple.checkpoint or {}
        channel_values = checkpoint_data.get("channel_values", {})
        messages = channel_values.get("messages", [])

        last_updated = (
            checkpoint_tuple.metadata.get("ts")
            if checkpoint_tuple.metadata
            else None
        ) or checkpoint_data.get("ts")
        last_updated_str = str(last_updated) if last_updated else None
        
        first_query = None
        for msg in messages:
            if isinstance(msg, HumanMessage) or getattr(msg, "type", "") == "human":
                first_query = msg.content
                break
            elif isinstance(msg, dict) and msg.get("type") in ("human", "user"):
                first_query = msg.get("content")
                break

        if not first_query:
            first_query = channel_values.get("query", "Empty Chat")
            
        first_query_str = str(first_query)
        title = first_query_str if len(first_query_str) <= 50 else f"{first_query_str[:47]}..."
        
        threads_summary.append(
            ThreadItem(
                thread_id=thread_id,
                title=title,
                last_updated=last_updated_str
            )
        )
    def parse_timestamp(item: ThreadItem) -> datetime:
        if not item.last_updated:
            return datetime.min
        try:
            return datetime.fromisoformat(item.last_updated)
        except ValueError:
            return datetime.min

    # 4. Sort descending (newest / most recently updated first)
    threads_summary.sort(key=parse_timestamp, reverse=True)
    return threads_summary


@app.get("/threads/{thread_id}/history", tags=["Thread History"])
def get_thread_history(thread_id: str, current_user: dict = Depends(get_current_user)):
    """Fetches full chat history for a specific thread_id."""
    username = current_user.get("username", "anonymous")
    # config = {
    #     "configurable": {
    #         "thread_id": thread_id,
    #         "checkpoint_ns": "",
    #         "metadata": {
    #             "user_id": current_user.get("username", "anonymous")
    #         }
    #     }
    # }
    try:

        logger.info(
            "Fetching chat history: username=%s",
            username,
        )

        messages = get_chat_history(
            username=username,
            thread_id=thread_id,
            limit=50,
        )

        logger.info(
            "Chat history loaded: username=%s messages=%s",
            username,
            len(messages),
        )

        return {
            "username": username,
            "thread_id": thread_id,
            "messages": messages,
        }

    except Exception as exc:

        logger.exception(
            "Failed to load chat history: username=%s",
            username
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
    # Retrieve current graph state snapshot
    # state = agent_app.get_state(config)
    
    # if not state or not state.values:
    #     raise HTTPException(status_code=404, detail="Thread not found")
        
    # messages = state.values.get("messages", [])
    # history = []

    # for m in messages:
    #     # Handle dict format (de-serialized checkpoints)
    #     if isinstance(m, dict):
    #         msg_type = m.get("type", "")
    #         role = "user" if msg_type in ("human", "user") else "assistant"
    #         content = m.get("content", "")
    #     # Handle LangChain Message objects
    #     else:
    #         msg_type = getattr(m, "type", "")
    #         if isinstance(m, HumanMessage) or msg_type in ("human", "user"):
    #             role = "user"
    #         else:
    #             role = "assistant"
    #         content = getattr(m, "content", "")

    #     history.append({"role": role, "content": content})

    # return history