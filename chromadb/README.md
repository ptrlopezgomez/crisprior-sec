# Base de datos vectorial (ChromaDB)

Almacena los embeddings de la base de conocimientos de seguridad (directrices,
políticas y reglas de contexto) usada por el motor de priorización (HU-04).

- `seed.py` — carga inicial de directrices de seguridad como documentos embebidos.
- El directorio `data/` (persistencia local de ChromaDB) está excluido del control
  de versiones vía `.gitignore`; cada desarrollador lo genera localmente ejecutando
  `python chromadb/seed.py`.
