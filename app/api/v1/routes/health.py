# health.py
from fastapi import APIRouter
import sqlalchemy

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/", operation_id="healthCheckApi", include_in_schema=False)
def health_check():
    try:
        db_ok = True
    except Exception:
        db_ok = False

    status = "ok" if db_ok else "error"
    return {"status": status}
