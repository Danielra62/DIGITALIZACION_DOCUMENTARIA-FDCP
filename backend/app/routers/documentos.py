from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.dependencies import get_current_user
from app.services.documento_service import guardar_documento
from app.services.documento_service import observar_alumno_service
from app.models.documento import Documento
from fastapi.responses import FileResponse
import os

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

@router.get("/ver/{doc_id}")
def ver_documento(doc_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc = db.query(Documento).filter(Documento.id == doc_id).first()

    if not doc:
        raise HTTPException(404, "Documento no encontrado")

    if not os.path.exists(doc.ruta_archivo):
        raise HTTPException(404, "Archivo no encontrado en el servidor")

    return FileResponse(
        doc.ruta_archivo,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={os.path.basename(doc.ruta_archivo)}"
        }
    )

@router.get("/descargar/{doc_id}")
def descargar(doc_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Aquí iría la lógica para servir el archivo físico con FileResponse
    # Por ahora es un placeholder para la URL del frontend
    doc = db.query(Documento).filter(Documento.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Documento no encontrado")
    
    return FileResponse(
        path=doc.ruta_archivo,
        filename=doc.nombre_original,
        media_type="application/pdf"
    )


@router.put("/alumnos/{alumno_id}/observar")
def observar_alumno(alumno_id: int, motivo: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return observar_alumno_service(db, alumno_id, motivo, user)