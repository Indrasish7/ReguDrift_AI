import os
from typing import Literal, Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Enterprise-scale configuration settings for ReguDrift AI.
    Loads configurations from environment variables or a local .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    # General App Config
    APP_NAME: str = "ReguDrift AI"
    ENV: Literal["local", "staging", "production"] = "local"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Google GenAI Settings
    GEMINI_API_KEY: SecretStr = Field(
        default=SecretStr("dummy_key_to_be_replaced_in_env"),
        description="Google Gemini GenAI API credential, securely masked as a SecretStr."
    )
    
    # Embedding Model Settings
    EMBEDDING_MODEL: str = Field(
        "gemini-embedding-001",
        description="Standard Google Gemini embedding model."
    )
    EMBEDDING_DIMENSION: int = Field(
        3072,
        description="Dimensionality of gemini-embedding-001."
    )


    # Vector Storage Settings
    VECTOR_STORE_PROVIDER: Literal["faiss", "qdrant"] = Field(
        "faiss",
        description="Active vector retrieval backend. Supported options: faiss, qdrant."
    )
    FAISS_INDEX_PATH: str = Field(
        "./data/faiss_index",
        description="Local directory path to store/load the FAISS CPU index binary."
    )
    QDRANT_URL: str = Field(
        "http://localhost:6333",
        description="Production Qdrant server endpoint url."
    )
    QDRANT_API_KEY: Optional[SecretStr] = Field(
        None,
        description="Secret token for authenticating against cloud/secure Qdrant instances."
    )
    DEFAULT_COLLECTION_NAME: str = Field(
        "regudrift_compliance_chunks",
        description="The target index collection name inside the vector store."
    )

    # Relational Persistence Settings
    DATABASE_URL: str = Field(
        "sqlite+aiosqlite:///./data/regudrift.db",
        description="Asynchronous database connection URL for storing historical audit trails."
    )



# Package-level instance initialization for clean imports
settings = Settings()

