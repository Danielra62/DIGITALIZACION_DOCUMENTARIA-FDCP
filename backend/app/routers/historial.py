from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.historial import Historial
from app.dependencies import require_role

router = APIRouter(prefix="/historial", tags=["Historial"])


@router.get("/")
def listar(db: Session = Depends(get_db),
           user=Depends(require_role("sistemas"))):
    
    return db.query(Historial).order_by(Historial.registrado_en.desc()).all()