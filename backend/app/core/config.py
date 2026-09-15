from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Directorio "backend/" (padre de "app/"), usado para anclar rutas por defecto
# que de otro modo dependerían del cwd desde el que se lance el proceso.
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "IaC Contextual Risk Prioritizer"
    api_v1_prefix: str = "/api/v1"

    chromadb_path: str = str(_BACKEND_DIR / "chromadb" / "data")
    chromadb_collection: str = "security_knowledge_base"

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    guideline_retrieval_count: int = 3

    # Umbral de reducción de fatiga por alertas (Objetivo General del TFM)
    alert_fatigue_reduction_target: float = 0.30

    # Validación de carga de archivos Terraform (HU-01)
    max_upload_size_bytes: int = 10 * 1024 * 1024


settings = Settings()
