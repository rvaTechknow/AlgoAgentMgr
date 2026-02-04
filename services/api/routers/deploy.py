"""Router stub."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_resources():
    return {"status": "stub", "resource": "deploy"}
