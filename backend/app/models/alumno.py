from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(11), unique=True, nullable=False)
    nombres = Column(String(120), nullable=False)
    apellidos = Column(String(120), nullable=False)
    anio_ingreso = Column(Integer, nullable=False) # Changed from YEAR to Integer as YEAR type is not directly supported by SQLAlchemy for all backends
    departamento = Column(String(80), nullable=False)
    
    id_escuela = Column(Integer, ForeignKey("escuelas.id"), nullable=False)
    id_digitalizador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    creado_en = Column(DateTime, default=func.now())
    estado = Column(Enum("pendiente", "observado", "aprobado", name="estado_alumno"), default="pendiente", nullable=False)
    
    aprobado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    aprobado_en = Column(DateTime, nullable=True)
    
    bloqueado = Column(Boolean, default=False, nullable=False)
    eliminado = Column(Boolean, default=False, nullable=False)
    eliminado_en = Column(DateTime, nullable=True)

    # Relationships
    escuela = relationship("Escuela")
    digitalizador = relationship("Usuario", foreign_keys=[id_digitalizador])
    aprobador = relationship("Usuario", foreign_keys=[aprobado_por])
    
    documentos = relationship("Documento", back_populates="alumno")
    observaciones = relationship("Observacion", back_populates="alumno")
