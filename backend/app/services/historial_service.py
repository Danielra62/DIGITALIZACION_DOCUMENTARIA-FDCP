from app.models.historial import Historial

def registrar_historial(
    db,
    user,
    accion: str,
    id_alumno=None,
    detalle=None,
    ip=None
):
    registro = Historial(
        id_usuario=user.id,
        correo=user.correo,
        tipo_usuario=user.rol.nombre,
        accion=accion,
        id_alumno=id_alumno,
        detalle=detalle,
        ip_origen=ip
    )

try:
    db.add(registro)
except Exception:
        pass  # o loggear