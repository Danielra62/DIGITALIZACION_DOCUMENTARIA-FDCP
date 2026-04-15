from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.dependencies import get_current_user
from app.services.documento_service import guardar_documento
from app.models.documento import Documento

router = APIRouter(prefix="/documentos", tags=["Documentos"])

@router.post("/{alumno_id}")
def subir(alumno_id: int, tipo: str, file: UploadFile,
          db: Session = Depends(get_db),
          user=Depends(get_current_user)):
    
    return guardar_documento(db, alumno_id, file, tipo, user)

@router.get("/alumno/{alumno_id}")
def listar_por_alumno(alumno_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Lógica de visibilidad básica
    docs = db.query(Documento).options(joinedload(Documento.subidor)).filter(Documento.id_alumno == alumno_id).all()
    return docs

@router.get("/descargar/{doc_id}")
def descargar(doc_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Aquí iría la lógica para servir el archivo físico con FileResponse
    # Por ahora es un placeholder para la URL del frontend
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Documento no encontrado")
    
    from fastapi.responses import FileResponse
    return FileResponse(doc.ruta_archivo, filename=doc.nombre_original)
