# Bootstrap del entorno de desarrollo (backend + frontend + ChromaDB) en Windows.
$ErrorActionPreference = "Stop"

Write-Host "== Backend =="
Set-Location backend
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
deactivate
Set-Location ..

Write-Host "== Frontend =="
Set-Location frontend
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
deactivate
Set-Location ..

Write-Host "== ChromaDB seed =="
& .\backend\.venv\Scripts\Activate.ps1
python chromadb\seed.py
deactivate

Write-Host "Listo. Backend: 'cd backend; uvicorn app.main:app --reload'"
Write-Host "Frontend: 'cd frontend; streamlit run app.py'"
