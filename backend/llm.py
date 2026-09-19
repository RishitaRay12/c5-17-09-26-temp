import os
import chromadb
# from langchain.agents import create_agent
# --- LlamaIndex & Vector DB Imports ---
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore


# from langchain_chroma import Chroma




from app.config import settings


def get_llm():


    # Complex tasks use Groq/OpenAI configuration
    provider = settings.LLM_PROVIDER

    if provider == "groq":

        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        return ChatOpenAI(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
            temperature=0.2,
        )

    if provider == "openai":

        if not settings.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0.2,
        )

    if provider == "ollama":

        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.2,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {provider}"
    )

# class LLM_Service:
#    def __init__(self):
#         model = os.getenv("LLM_MODEL")
#         api_key = os.getenv("LLM_KEY")
#         url = os.getenv("BASIC_URL")

#         self.llm = ChatOpenAI(model=model, api_key=api_key, base_url=url)


# A. LlamaIndex Semantic Splitter RAG Setup
def setup_semantic_rag():
    embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("retail_policies")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    if chroma_collection.count() == 0:
        from llama_parse import LlamaParse
        parser = LlamaParse(
            result_type="markdown",       # Preserves tables as Markdown tables
            tier="agentic",               # Uses the agentic tier for accurate layout/table extraction
            version="latest",             # Required when specifying a tier
            api_key=os.getenv("LLAMA_CLOUD_API_KEY")
        )
        documents = SimpleDirectoryReader("./Documents", file_extractor={".pdf": parser}).load_data()
        
        semantic_splitter = SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            embed_model=embed_model
        )
        nodes = semantic_splitter.get_nodes_from_documents(documents)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(nodes, storage_context=storage_context, embed_model=embed_model)
    else:
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
        
    return index.as_retriever(similarity_top_k=3)

