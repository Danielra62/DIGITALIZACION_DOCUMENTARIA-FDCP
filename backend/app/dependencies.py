from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.database import SessionLocal
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user

def require_role(role: str):
    def role_checker(user: Usuario = Depends(get_current_user)):
        if user.rol.nombre != role:
            raise HTTPException(status_code=403, detail="No autorizado")
        return user
    return role_checker