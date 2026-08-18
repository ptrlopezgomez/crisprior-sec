"""Carga inicial de la base de conocimientos de seguridad en ChromaDB (HU-04).

Uso:
    python chromadb/seed.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.engine.vector_store import get_collection  # noqa: E402

SECURITY_GUIDELINES = [
    {
        "id": "guideline-001",
        "document": "Un puerto SSH (22) o RDP (3389) abierto a 0.0.0.0/0 sin aislamiento "
        "de red representa una exposición crítica salvo que exista un Bastion Host "
        "o VPN como control compensatorio.",
        "metadata": {"category": "network_exposure", "service": "virtual_machine"},
    },
    {
        "id": "guideline-002",
        "document": "Un Storage Account con acceso público habilitado pero restringido "
        "exclusivamente a una VNet privada reduce sustancialmente el riesgo real "
        "de exfiltración de datos.",
        "metadata": {"category": "network_exposure", "service": "storage"},
    },
]


def seed() -> None:
    collection = get_collection()
    collection.upsert(
        ids=[g["id"] for g in SECURITY_GUIDELINES],
        documents=[g["document"] for g in SECURITY_GUIDELINES],
        metadatas=[g["metadata"] for g in SECURITY_GUIDELINES],
    )
    print(f"Cargadas {len(SECURITY_GUIDELINES)} directrices en la colección.")


if __name__ == "__main__":
    seed()
