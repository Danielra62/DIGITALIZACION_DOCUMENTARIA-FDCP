from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models.documento import Documento
from app.models.alumno import Alumno
from app.services.storage_service import guardar_archivo
from app.services.historial_service import registrar_historial
import os

def guardar_documento(db: Session, alumno_id: int, file: UploadFile, tipo: str, user):

    alumno = db.query(Alumno).filter(
        Alumno.id == alumno_id,
        Alumno.eliminado == False
    ).first()

    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    # 🔒 Validar PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    # 🔒 Validar roles
    if user.rol.nombre in ["sistemas", "usuario"]:
        raise HTTPException(status_code=403, detail="Rol no autorizado")

    # =========================
    # 📌 DIGITALIZADOR
    # =========================
    if user.rol.nombre == "digitalizador":

        if tipo != "digitalizador":
            raise HTTPException(status_code=403, detail="Solo tipo digitalizador")

        if alumno.id_digitalizador != user.id:
            raise HTTPException(status_code=403, detail="No autorizado")

        if alumno.estado not in ["pendiente", "observado"]:
            raise HTTPException(status_code=400, detail="Solo en pendiente u observado")

        # 🔥 si estaba observado, vuelve a pendiente
        if alumno.estado == "observado":
            alumno.estado = "pendiente"

    # =========================
    # 📌 ADMINISTRATIVO
    # =========================
    elif user.rol.nombre == "administrativo":

        if tipo != "acta":
            raise HTTPException(status_code=403, detail="Solo tipo acta")

        if alumno.estado != "pendiente":
            raise HTTPException(status_code=400, detail="Solo en pendiente")

        # Debe existir documento del digitalizador
        doc_digitalizador = db.query(Documento).filter(
            Documento.id_alumno == alumno_id,
            Documento.tipo == "digitalizador"
        ).first()

        if not doc_digitalizador:
            raise HTTPException(400, "Debe existir documento del digitalizador")

        # Evitar duplicado de acta
        doc_acta = db.query(Documento).filter(
            Documento.id_alumno == alumno_id,
            Documento.tipo == "acta"
        ).first()

        if doc_acta:
            raise HTTPException(400, "El acta ya existe")

    # =========================
    # 🧠 GENERAR NOMBRE (ANTES DE TODO)
    # =========================
    nombre_estandarizado = f"{'REG' if tipo == 'digitalizador' else 'ACT'}-{alumno.codigo}.pdf"

    # =========================
    # 📁 GUARDAR ARCHIVO
    # =========================
    ruta_guardado = guardar_archivo(alumno, file, tipo, nombre_estandarizado)

    # =========================
    # 💾 DB
    # =========================
    doc = db.query(Documento).filter(
        Documento.id_alumno == alumno_id,
        Documento.tipo == tipo
    ).first()

    ruta_guardado = guardar_archivo(alumno, file, tipo, nombre_estandarizado)

    if doc:
        doc.ruta_archivo = ruta_guardado
        doc.nombre_original = nombre_estandarizado
        doc.tamanio_bytes = file.size
        doc.subido_por = user.id
    else:
        doc = Documento(
            id_alumno=alumno_id,
            tipo=tipo,
            ruta_archivo=ruta_guardado,
            nombre_original=nombre_estandarizado,
            tamanio_bytes=file.size,
            subido_por=user.id
        )
        db.add(doc)

    db.commit()
    db.refresh(doc)

    registrar_historial(
        db,
        user,
        "SUBIR_DOCUMENTO",
        alumno.id,
        {
            "tipo": tipo,
            "nombre_archivo": nombre_estandarizado  # 🔥 ya no uses file.filename
        }
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

def observar_alumno_service(db: Session, alumno_id: int, motivo: str, user):

    alumno = db.query(Alumno).filter(
        Alumno.id == alumno_id,
        Alumno.eliminado == False
    ).first()

    if not alumno:
        raise HTTPException(404, "Alumno no encontrado")

    # 🔒 Solo administrativo
    if user.rol.nombre != "administrativo":
        raise HTTPException(403, "No autorizado")

    # 🔒 Solo si está en revisión (pendiente)
    if alumno.estado != "pendiente":
        raise HTTPException(400, "Solo se puede observar en estado pendiente")

    # 🔥 CAMBIO DE ESTADO
    alumno.estado = "observado"

    db.commit()
    db.refresh(alumno)

    # 🧾 HISTORIAL
    registrar_historial(
        db,
        user,
        "SUBSANAR_OBSERVACION",
        alumno.id,
        {"comentario": "Se corrigió la observación"}
    )

    return alumno