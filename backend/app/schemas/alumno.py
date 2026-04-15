from pydantic import BaseModel
from typing import Optional

class AlumnoCreate(BaseModel):
    codigo: str
    nombres: str
    apellidos: str
    anio_ingreso: int
    departamento: str
    id_escuela: int

class AlumnoUpdate(BaseModel):
    nombres: Optional[str]
    apellidos: Optional[str]
    departamento: Optional[str]
    id_escuela: Optional[int]

class AlumnoResponse(BaseModel):
    id: int
    codigo: str
    nombres: str
    apellidos: str
    estado: str

    class Config:
        from_attributes = True