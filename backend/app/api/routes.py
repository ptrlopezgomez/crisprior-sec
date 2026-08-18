from fastapi import APIRouter, UploadFile

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/scan")
async def scan_terraform(files: list[UploadFile]) -> dict[str, str]:
    """Recibe archivos .tf, ejecuta Checkov/tfsec y devuelve el baseline (HU-01, HU-02).

    TODO (Sprint 1): validar extensión/tamaño (10MB), persistir temporalmente
    y delegar a app.scanners.
    """
    return {"status": "not_implemented", "files_received": str(len(files))}
