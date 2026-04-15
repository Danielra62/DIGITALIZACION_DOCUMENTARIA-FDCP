from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.alumno import AlumnoCreate, AlumnoUpdate
from app.models.alumno import Alumno
from app.dependencies import get_current_user
from app.dependencies import require_role

from app.services import alumno_service


router = APIRouter(prefix="/alumnos", tags=["Alumnos"])

@router.post("/")
def crear(data: AlumnoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return alumno_service.crear_alumno(db, data, user)


@router.get("/")
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return alumno_service.listar_alumnos(db, user)


@router.get("/{id}")
def obtener(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return alumno_service.obtener_alumno_por_id(db, id, user)


@router.put("/{id}")
def editar(id: int, data: AlumnoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return alumno_service.editar_alumno(db, id, data, user)


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return alumno_service.eliminar_alumno(db, id, user)


@router.post("/{id}/observar")
def observar(id: int, comentario: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return alumno_service.observar_alumno(db, id, comentario, user)


@router.post("/{id}/aprobar")
def aprobar(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return alumno_service.aprobar_alumno(db, id, user)
