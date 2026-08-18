#!/usr/bin/env bash
# Bootstrap del entorno de desarrollo (backend + frontend + ChromaDB).
set -euo pipefail

echo "== Backend =="
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp -n .env.example .env || true
deactivate
cd ..

echo "== Frontend =="
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

echo "== ChromaDB seed =="
source backend/.venv/bin/activate
python chromadb/seed.py
deactivate

echo "Listo. Backend: 'cd backend && uvicorn app.main:app --reload'"
echo "Frontend: 'cd frontend && streamlit run app.py'"
