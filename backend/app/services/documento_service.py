from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models.documento import Documento
from app.models.alumno import Alumno
from app.services.storage_service import guardar_archivo
from app.services.historial_service import registrar_historial
import os

def guardar_documento(db: Session, alumno_id: int, file: UploadFile, tipo: str, user):
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id, Alumno.eliminado == False).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    # Validar rol para subir documentos
    if user.rol.nombre == "digitalizador" and tipo != "digitalizador":
        raise HTTPException(status_code=403, detail="Digitalizadores solo pueden subir documentos de tipo 'digitalizador'")
    
    if user.rol.nombre == "administrativo" and tipo != "acta":
        raise HTTPException(status_code=403, detail="Administrativos solo pueden subir documentos de tipo 'acta'")
    
    if user.rol.nombre == "sistemas" or user.rol.nombre == "usuario":
        raise HTTPException(status_code=403, detail="Rol no autorizado para subir documentos")

    # Validar extensión PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    # Contar documentos existentes para el alumno
    documentos_existentes = db.query(Documento).filter(Documento.id_alumno == alumno_id).count()

    if user.rol.nombre == "digitalizador":
        if documentos_existentes >= 1:
            raise HTTPException(status_code=400, detail="El digitalizador solo puede subir un documento inicial por alumno.")
        # Asegurarse de que el digitalizador solo sube para sus propios alumnos
        if alumno.id_digitalizador != user.id:
            raise HTTPException(status_code=403, detail="No autorizado para subir documentos a este alumno")
        if alumno.estado != "pendiente":
            raise HTTPException(status_code=440, detail="Solo se pueden subir documentos a alumnos en estado pendiente")

    elif user.rol.nombre == "administrativo":
        if documentos_existentes >= 2:
            raise HTTPException(status_code=400, detail="Ya existen dos documentos para este alumno. No se pueden subir más.")
        # Asegurarse de que el administrativo sube el acta para un alumno pendiente
        if alumno.estado != "pendiente":
            raise HTTPException(status_code=400, detail="Solo se pueden subir actas a alumnos en estado pendiente")

    # Guardar archivo físicamente
    ruta_guardado = guardar_archivo(alumno_id, file, tipo)

    # Crear o actualizar registro de documento en DB
    doc = db.query(Documento).filter(Documento.id_alumno == alumno_id, Documento.tipo == tipo).first()
    if doc:
        # Si ya existe un documento del mismo tipo, lo actualizamos (ej. si el digitalizador resube)
        doc.ruta_archivo = ruta_guardado
        doc.nombre_original = file.filename
        doc.tamanio_bytes = file.size
        doc.subido_por = user.id
    else:
        doc = Documento(
            id_alumno=alumno_id,
            tipo=tipo,
            ruta_archivo=ruta_guardado,
            nombre_original=file.filename,
            tamanio_bytes=file.size,
            subido_por=user.id
        )
        db.add(doc)
    
    db.commit()
    db.refresh(doc)

    registrar_historial(
        db, user,
        "SUBIR_DOCUMENTO",
        alumno.id,
        {"tipo": tipo, "nombre_archivo": file.filename}
    )

    return doc


def obtener_documentos_alumno(db: Session, alumno_id: int, user):
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id, Alumno.eliminado == False).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    # Lógica de visibilidad para documentos
    if user.rol.nombre == "digitalizador" and alumno.id_digitalizador != user.id:
        raise HTTPException(status_code=403, detail="No autorizado para ver documentos de este alumno")
    
    if user.rol.nombre == "usuario" and alumno.estado != "aprobado":
        raise HTTPException(status_code=403, detail="No autorizado para ver documentos de este alumno (solo aprobados)")

    return db.query(Documento).filter(Documento.id_alumno == alumno_id).all()
