from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    id_alumno = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False)

    tipo = Column(Enum("digitalizador", "acta", name="tipo_documento"), nullable=False)

    ruta_archivo = Column(String(500), nullable=False)
    nombre_original = Column(String(255), nullable=False)
    tamanio_bytes = Column(Integer, nullable=False)

    subido_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    subido_en = Column(DateTime, default=func.now())

    alumno = relationship("Alumno", back_populates="documentos")
    subidor = relationship("Usuario")
