"""Cliente HTTP delgado hacia el backend FastAPI."""

import json
from typing import Callable

import requests

BACKEND_URL = "http://localhost:8000/api/v1"

# El análisis invoca Checkov/trivy y, por cada hallazgo, al LLM local
# (Ollama); con varios hallazgos la respuesta puede tardar más que una
# petición HTTP típica.
_SCAN_TIMEOUT_SECONDS = 600


def scan_files(uploaded_files: list, on_progress: Callable[[dict], None] | None = None) -> dict:
    """Envía los archivos .tf cargados en Streamlit al endpoint `/scan` del backend.

    La respuesta es NDJSON: una línea por evento de progreso y una línea
    final `{"type": "result", "data": <ScanResponse>}`. Cada evento se
    reporta a `on_progress` (si se pasa) a medida que llega, en vez de
    esperar en silencio a que termine todo el análisis.
    """
    files = [("files", (f.name, f.getvalue(), f.type or "text/plain")) for f in uploaded_files]

    with requests.post(
        f"{BACKEND_URL}/scan", files=files, stream=True, timeout=_SCAN_TIMEOUT_SECONDS
    ) as response:
        response.raise_for_status()

        result: dict | None = None
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            event = json.loads(line)
            event_type = event.get("type")

            if event_type == "result":
                result = event["data"]
            elif event_type == "error":
                raise RuntimeError(event.get("message", "Error desconocido durante el análisis"))
            elif on_progress:
                on_progress(event)

        if result is None:
            raise RuntimeError("El backend cerró la conexión sin devolver un resultado")
        return result
