import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Central application configuration."""

    # Application
    # APP_NAME = "AI Startup Co-Founder Team"
    # HOST = "0.0.0.0"
    # PORT = 8000
    # DEBUG_MODE = True

    # SECRET_KEY = "YOUR_SUPER_SECRET_KEY_CHANGE_THIS_IN_PRODUCTION"
    # ALGORITHM = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES = 60
        
    # LLM provider
    # openai / gemini / ollama
    LLM_PROVIDER = os.getenv(
        "LLM_PROVIDER",
        "openai",
    ).lower()

    # OpenAI
    # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # OPENAI_MODEL = os.getenv(
    #     "OPENAI_MODEL",
    #     "gpt-5-mini",
    # )
    # OPENAI_BASE_URL = os.getenv(
    #     "OPENAI_BASE_URL",
    #     "https://api.openai.com/v1",
    # )

    # -----------------------------------------
    # Groq
    # -----------------------------------------
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "qwen3.6-27b",
    )

    GROQ_BASE_URL = os.getenv(
        "GROQ_BASE_URL",
        "https://api.groq.com/openai/v1",
    )

    # Ollama
    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    )
    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "llama3.1:8b",
    )
    DB_FILE = "retail_compliance.db"
    SECRET_KEY = "YOUR_SUPER_SECRET_KEY_CHANGE_THIS_IN_PRODUCTION"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    # Database
    # DATABASE_PATH = os.getenv(
    #     "DATABASE_PATH",
    #     "startup.db",
    # )
    # DB_PATH = os.getenv(
    #     "DB_PATH",
    #     "app.db",
    # )
    # # -----------------------------------------
    # # LangGraph checkpoint database
    # # -----------------------------------------
    # CHECKPOINT_DATABASE_PATH = os.getenv(
    #     "CHECKPOINT_DATABASE_PATH",
    #     "startup_checkpoints.db",
    # )

    # # CORS
    # CORS_ORIGINS = os.getenv(
    #     "CORS_ORIGINS",
    #     "http://localhost:5173",
    # ).split(",")


settings = Settings()