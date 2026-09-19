import tempfile
from chromadb.utils import embedding_functions
import re
import chromadb
from typing import Iterable
from fastapi import UploadFile, HTTPException
from schema import UploadResponse
import logging
import os
from parse_tables import parse_pdf_tables

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # 384 dimensions
)
collection = chromadb.PersistentClient(path="./chroma_db").get_or_create_collection("retail_policies", embedding_function=ef)

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> list[str]:
    if not text or not text.strip():
        return []

    words = re.findall(r"\S+", text)
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end == len(words):
            break
        start = max(start + chunk_size - chunk_overlap, start + 1)

    return chunks


def _add_chunks_to_collection(collection: chromadb.Collection, filename: str, chunks: Iterable[str], chunk_type: str = "text") -> int:
    documents_to_add: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    for idx, chunk in enumerate(chunks):
        if not chunk or not chunk.strip():
            continue
        chunk_id = f"{filename}_chunk_{idx}"
        documents_to_add.append(chunk)
        ids.append(chunk_id)
        metadatas.append(
            {
                "source": filename,
                "chunk_index": idx,
                "type": chunk_type,
            }
        )

    if documents_to_add:
        collection.add(
            documents=documents_to_add,
            metadatas=metadatas,
            ids=ids,
        )

    return len(documents_to_add)


async def _process_uploaded_files(files: list[UploadFile]) -> list[UploadResponse]:
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    results: list[UploadResponse] = []
    supported_extensions = {".pdf", ".txt", ".md", ".csv", ".json"}

    for uploaded_file in files:
        filename = uploaded_file.filename or "uploaded_file"
        extension = os.path.splitext(filename)[1].lower()

        if extension not in supported_extensions:
            logger.info("Skipping unsupported file: %s", filename)
            continue

        try:
            payload = await uploaded_file.read()
            if extension == ".pdf":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(payload)
                    temp_path = temp_file.name

                try:
                    full_text, dataframes = parse_pdf_tables(temp_path)
                    text_chunks = chunk_text(full_text)
                    table_chunks = [df.to_markdown(index=False) for df in dataframes]
                    documents_added = _add_chunks_to_collection(collection,filename, text_chunks, "text")
                    documents_added += _add_chunks_to_collection(collection, filename, table_chunks, "table")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                content = payload.decode("utf-8", errors="ignore")
                documents_added = _add_chunks_to_collection(collection, filename, chunk_text(content), "text")

            results.append(
                UploadResponse(
                    filename=filename,
                    status="success",
                    files_processed=1,
                    documents_added=documents_added,
                )
            )
        except Exception as exc:
            logger.exception("Failed to process uploaded file: %s", filename)
            results.append(
                UploadResponse(
                    filename=filename,
                    status=f"failed: {str(exc)}",
                    files_processed=1,
                    documents_added=0,
                )
            )

    if not results:
        raise HTTPException(
            status_code=400,
            detail="No supported files were received. Supported types: .pdf, .txt, .md, .csv, .json",
        )

    return results