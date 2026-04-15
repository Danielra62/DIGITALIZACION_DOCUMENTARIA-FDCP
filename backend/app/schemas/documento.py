from pydantic import BaseModel

class DocumentoResponse(BaseModel):
    id: int
    tipo: str
    nombre_original: str

    class Config:
        from_attributes = True