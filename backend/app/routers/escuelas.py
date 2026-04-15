from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.escuela import Escuela

router = APIRouter(prefix="/escuelas", tags=["Escuelas"])

@router.get("/")
def listar_escuelas(db: Session = Depends(get_db)):
    return db.query(Escuela).filter(Escuela.activa == True).all()
