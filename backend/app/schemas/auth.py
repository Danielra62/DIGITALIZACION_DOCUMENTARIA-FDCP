from pydantic import BaseModel

class LoginRequest(BaseModel):
    correo: str
    password: str