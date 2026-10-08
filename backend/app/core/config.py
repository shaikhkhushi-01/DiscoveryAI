from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    app_env: str = Field(default="development")
    app_name: str = Field(default="DiscoveryAI")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    database_url: str = Field(default="postgresql://postgres:postgres@localhost:5432/discoveryai")
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_username: str = Field(default="neo4j")
    neo4j_password: SecretStr = Field(default=SecretStr("change-me"))
    neo4j_database: str = Field(default="neo4j")
    qdrant_url: str = Field(default="http://localhost:6333")
    redis_url: str = Field(default="redis://localhost:6379/0")
    cors_origins: str = Field(default="http://localhost:3000")
    llm_provider: str = Field(default="ollama")
    ollama_base_url: str = Field(default="http://localhost:11434")
    openai_api_key: SecretStr | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    gemini_api_key: SecretStr | None = Field(default=None)
    gemini_model: str = Field(default="gemini-3.5-flash-lite")
    gemini_base_url: str = Field(default="https://generativelanguage.googleapis.com/v1beta")
    embedding_provider: str = Field(default="sentence-transformers")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384, ge=1)
    qdrant_collection: str = Field(default="scientific_chunks")
    reranker_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    jwt_secret_key: SecretStr = Field(default=SecretStr("development-only-change-me"))
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
