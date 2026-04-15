from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.services.auth_service import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.correo == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # 👇 ASEGURAR que el rol esté cargado
    if not user.rol:
        raise HTTPException(status_code=500, detail="Usuario sin rol asignado")

    # 👇 INCLUIR ROL EN EL TOKEN
    token = create_access_token({
        "sub": str(user.id),
        "rol": user.rol.nombre   # 🔥 CLAVE
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }