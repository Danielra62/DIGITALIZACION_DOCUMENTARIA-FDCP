from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    correo: EmailStr
    nombre_display: str
    password: str
    rol: str

class RolResponse(BaseModel):
    nombre: str
    class Config:
        from_attributes = True

class UsuarioResponse(BaseModel):
    id: int
    correo: EmailStr
    nombre_display: str
    rol: RolResponse

    class Config:
        from_attributes = True
