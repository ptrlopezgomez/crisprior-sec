"""Cliente HTTP delgado hacia el backend FastAPI."""

import requests

BACKEND_URL = "http://localhost:8000/api/v1"


def scan_files(files: list) -> dict:
    response = requests.post(f"{BACKEND_URL}/scan", files=files, timeout=30)
    response.raise_for_status()
    return response.json()
