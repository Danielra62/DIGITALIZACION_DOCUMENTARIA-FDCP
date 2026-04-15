from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.models.roles import Rol
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.dependencies import require_role
from app.services.auth_service import hash_password
from app.services.historial_service import registrar_historial

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# 🔍 LISTAR USUARIOS (solo sistemas)
@router.get("/", response_model=list[UsuarioResponse])
def listar(db: Session = Depends(get_db),
           user=Depends(require_role("sistemas"))):

    return db.query(Usuario).all()


# 🔥 CREAR USUARIO
@router.post("/", response_model=UsuarioResponse)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("sistemas"))
):
    # 🔒 Validar correo único
    existe = db.query(Usuario).filter(Usuario.correo == data.correo).first()
    if existe:
        raise HTTPException(400, "El correo ya está registrado")

    # 🔒 Validar rol existente
    rol = db.query(Rol).filter(Rol.nombre == data.rol).first()
    if not rol:
        raise HTTPException(400, "Rol inválido")

    # 🔐 Crear usuario
    nuevo = Usuario(
        correo=data.correo,
        nombre_display=data.nombre_display,
        password_hash=hash_password(data.password),
        id_rol=rol.id
    )

    db.add(nuevo)
    db.flush()  # para obtener ID antes del commit

    # 📜 Auditoría
    registrar_historial(
        db,
        user,
        "CREAR_USUARIO",
        detalle={
            "correo": data.correo,
            "rol": data.rol
        }
    )

    db.commit()
    db.refresh(nuevo)

    return nuevo