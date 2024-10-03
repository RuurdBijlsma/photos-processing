from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from photos.database.database import get_session

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_session)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database connection error")
