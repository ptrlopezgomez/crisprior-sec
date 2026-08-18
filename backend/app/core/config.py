from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "IaC Contextual Risk Prioritizer"
    api_v1_prefix: str = "/api/v1"

    chromadb_path: str = "./chromadb/data"
    chromadb_collection: str = "security_knowledge_base"

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Umbral de reducción de fatiga por alertas (Objetivo General del TFM)
    alert_fatigue_reduction_target: float = 0.30


settings = Settings()
