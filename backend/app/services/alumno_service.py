from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from sqlalchemy.sql import func

from app.models.alumno import Alumno
from app.models.observacion import Observacion
from app.models.documento import Documento
from app.models.historial import Historial
from app.services.historial_service import registrar_historial


# ===============================
# 🔥 HELPERS INTERNOS
# ===============================

def _get_alumno_model(db: Session, alumno_id: int):
    alumno = db.query(Alumno).options(
        joinedload(Alumno.escuela),
        joinedload(Alumno.digitalizador),
        joinedload(Alumno.aprobador),
        joinedload(Alumno.observaciones)
    ).filter(
        Alumno.id == alumno_id,
        Alumno.eliminado == False
    ).first()

    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    return alumno


def _build_alumno_response(alumno: Alumno):
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
        "anio_ingreso": alumno.anio_ingreso,
        "departamento": alumno.departamento,
        "escuela": alumno.escuela,
        "digitalizador": alumno.digitalizador,
        "aprobador": alumno.aprobador
    }


# ===============================
# 🚀 CRUD
# ===============================

def crear_alumno(db: Session, data, user):
    if user.rol.nombre != "digitalizador":
        raise HTTPException(403, "Solo los digitalizadores pueden crear alumnos")

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
        pass
    elif user.rol.nombre == "digitalizador":
        query = query.filter(Alumno.id_digitalizador == user.id)
    elif user.rol.nombre == "administrativo":
        query = query.filter(Alumno.estado == "pendiente")
    elif user.rol.nombre == "usuario":
        query = query.filter(Alumno.estado == "aprobado")
    else:
        raise HTTPException(403, "Rol no autorizado")

    alumnos = query.options(
        joinedload(Alumno.escuela),
        joinedload(Alumno.digitalizador),
        joinedload(Alumno.aprobador)
    ).all()

    return [
        {
            "id": a.id,
            "codigo": a.codigo,
            "nombres": a.nombres,
            "apellidos": a.apellidos,
            "estado": a.estado,
            "creado_en": a.creado_en,
            "aprobado_en": a.aprobado_en,
            "digitalizador": a.digitalizador,
            "aprobador": a.aprobador
        }
        for a in alumnos
    ]


def obtener_alumno_por_id(db: Session, alumno_id: int, user):
    alumno = _get_alumno_model(db, alumno_id)

    # 🔐 control acceso
    if user.rol.nombre == "digitalizador" and alumno.id_digitalizador != user.id:
        raise HTTPException(403, "No autorizado")

    if user.rol.nombre == "usuario" and alumno.estado != "aprobado":
        raise HTTPException(403, "No autorizado")

    return _build_alumno_response(alumno)


def editar_alumno(db: Session, alumno_id: int, data, user):
    alumno = _get_alumno_model(db, alumno_id)

    if alumno.estado == "aprobado":
        raise HTTPException(400, "No se puede editar un registro aprobado")

    # 🔥 actualizar campos
    for key, value in data.dict(exclude_unset=True).items():
        setattr(alumno, key, value)

    # 🔥 SUBSANACIÓN AUTOMÁTICA
    db.query(Observacion).filter(
        Observacion.id_alumno == alumno.id,
        Observacion.activa == True
    ).update({"activa": False})

    # 🔥 eliminar historial de observación
    db.query(Historial).filter(
        Historial.id_alumno == alumno.id,
        Historial.accion == "OBSERVAR_ALUMNO"
    ).delete()

    # 🔥 volver a pendiente si estaba observado
    if alumno.estado == "observado":
        alumno.estado = "pendiente"

    db.commit()
    db.refresh(alumno)

    registrar_historial(db, user, "EDITAR_ALUMNO", alumno.id)
    return alumno


def eliminar_alumno(db: Session, alumno_id: int, user):
    alumno = _get_alumno_model(db, alumno_id)

    if alumno.estado == "aprobado":
        raise HTTPException(400, "No se puede eliminar un registro aprobado")

    alumno.eliminado = True
    db.commit()

    registrar_historial(db, user, "ELIMINAR_ALUMNO", alumno.id)
    return {"ok": True}


# ===============================
# 🔍 FLUJO DE APROBACIÓN
# ===============================

def observar_alumno(db: Session, alumno_id: int, comentario: str, user):
    alumno = _get_alumno_model(db, alumno_id)

    if user.rol.nombre != "administrativo":
        raise HTTPException(403, "Solo administrativos pueden observar")

    if alumno.estado == "aprobado":
        raise HTTPException(400, "No se puede observar un alumno aprobado")

    # cambiar estado
    alumno.estado = "observado"

    # desactivar anteriores
    db.query(Observacion).filter(
        Observacion.id_alumno == alumno.id,
        Observacion.activa == True
    ).update({"activa": False})

    # nueva observación
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
    alumno = _get_alumno_model(db, alumno_id)

    if user.rol.nombre != "administrativo":
        raise HTTPException(403, "Solo administrativos pueden aprobar")

    # verificar acta
    acta = db.query(Documento).filter(
        Documento.id_alumno == alumno.id,
        Documento.tipo == "acta"
    ).first()

    if not acta:
        raise HTTPException(400, "Debe subir el acta antes de aprobar")

    alumno.estado = "aprobado"
    alumno.aprobado_por = user.id
    alumno.aprobado_en = func.now()

    db.commit()

    registrar_historial(db, user, "APROBAR_ALUMNO", alumno.id)
    return alumno