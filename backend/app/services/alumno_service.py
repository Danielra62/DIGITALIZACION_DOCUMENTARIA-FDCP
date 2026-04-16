from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models.alumno import Alumno
from app.models.observacion import Observacion
from app.models.documento import Documento
from app.services.historial_service import registrar_historial
from sqlalchemy.sql import func

def crear_alumno(db: Session, data, user):
    if user.rol.nombre != "digitalizador":
        raise HTTPException(status_code=403, detail="Solo los digitalizadores pueden crear alumnos")
    
    alumno = Alumno(
        codigo=data.codigo,
        nombres=data.nombres.upper(),
        apellidos=data.apellidos.upper(),
        anio_ingreso=data.anio_ingreso,
        departamento=data.departamento.upper(),
        id_escuela=data.id_escuela,
        id_digitalizador=user.id,
        estado="pendiente"
    )

    db.add(alumno)
    db.commit()
    db.refresh(alumno)

    registrar_historial(db, user, "CREAR_ALUMNO", alumno.id, {"codigo": alumno.codigo})
    return alumno

def listar_alumnos(db: Session, user):
    query = db.query(Alumno).filter(Alumno.eliminado == False)

    if user.rol.nombre == "sistemas":
        # Sistemas ve todo
        pass
    elif user.rol.nombre == "digitalizador":
        query = query.filter(Alumno.id_digitalizador == user.id)
    elif user.rol.nombre == "administrativo":
        query = query.filter(Alumno.estado == "pendiente")
    elif user.rol.nombre == "usuario":
        query = query.filter(Alumno.estado == "aprobado")
    else:
        raise HTTPException(status_code=403, detail="Rol no autorizado")

    return query.options(joinedload(Alumno.escuela), joinedload(Alumno.digitalizador), joinedload(Alumno.aprobador)).all()

def obtener_alumno_por_id(db: Session, alumno_id: int, user):
    alumno = db.query(Alumno).options(
        joinedload(Alumno.escuela), 
        joinedload(Alumno.digitalizador), 
        joinedload(Alumno.aprobador),
        joinedload(Alumno.observaciones)  # 👈 IMPORTANTE
    ).filter(
        Alumno.id == alumno_id,
        Alumno.eliminado == False
    ).first()
    
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # 🔥 obtener observación activa
    observacion_activa = next(
        (o for o in alumno.observaciones if o.activa),
        None
    )

    return {
        "id": alumno.id,
        "codigo": alumno.codigo,
        "nombres": alumno.nombres,
        "apellidos": alumno.apellidos,
        "estado": alumno.estado,
        "observacion": observacion_activa.comentario if observacion_activa else None,

        # 👇 incluye lo que ya usas en frontend
        "anio_ingreso": alumno.anio_ingreso,
        "departamento": alumno.departamento,
        "escuela": alumno.escuela,
        "digitalizador": alumno.digitalizador,
        "aprobador": alumno.aprobador
    }

def editar_alumno(db: Session, alumno_id: int, data, user):
    alumno = obtener_alumno_por_id(db, alumno_id, user)
    
    if alumno.estado == "aprobado":
        raise HTTPException(status_code=400, detail="No se puede editar un registro aprobado")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(alumno, key, value)

    db.commit()
    db.refresh(alumno)
    registrar_historial(db, user, "EDITAR_ALUMNO", alumno.id)
    return alumno

def eliminar_alumno(db: Session, alumno_id: int, user):
    alumno = obtener_alumno_por_id(db, alumno_id, user)
    
    if alumno.estado == "aprobado":
        raise HTTPException(status_code=400, detail="No se puede eliminar un registro aprobado")

    alumno.eliminado = True
    db.commit()
    registrar_historial(db, user, "ELIMINAR_ALUMNO", alumno.id)
    return {"ok": True}

def observar_alumno(db: Session, alumno_id: int, comentario: str, user):
    alumno = obtener_alumno_por_id(db, alumno_id, user)

    if user.rol.nombre != "administrativo":
        raise HTTPException(403, "Solo administrativos pueden observar")

    if alumno.estado == "aprobado":
        raise HTTPException(400, "No se puede observar un alumno aprobado")

    # Cambiar estado
    alumno.estado = "observado"

    # Desactivar observaciones anteriores
    db.query(Observacion).filter(
        Observacion.id_alumno == alumno.id,
        Observacion.activa == True
    ).update({"activa": False})

    # Crear nueva observación
    obs = Observacion(
        id_alumno=alumno.id,
        comentario=comentario,
        id_creado_por=user.id
    )

    db.add(obs)
    db.commit()

    registrar_historial(
        db,
        user,
        "OBSERVAR_ALUMNO",
        alumno.id,
        {"comentario": comentario}
    )

    return alumno

def aprobar_alumno(db: Session, alumno_id: int, user):
    alumno = obtener_alumno_por_id(db, alumno_id, user)
    if user.rol.nombre != "administrativo":
        raise HTTPException(403, "Solo administrativos pueden aprobar")

    # Verificar que exista el acta
    acta = db.query(Documento).filter(Documento.id_alumno == alumno.id, Documento.tipo == "acta").first()
    if not acta:
        raise HTTPException(400, "Debe subir el acta antes de aprobar")

    alumno.estado = "aprobado"
    alumno.aprobado_por = user.id
    alumno.aprobado_en = func.now()
    db.commit()
    registrar_historial(db, user, "APROBAR_ALUMNO", alumno.id)
    return alumno
