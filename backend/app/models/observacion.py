from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Boolean
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Observacion(Base):
    __tablename__ = "observaciones"

    id = Column(Integer, primary_key=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"))
    alumno = relationship("Alumno", back_populates="observaciones")

    comentario = Column(Text, nullable=False)

    creado_por = Column(Integer, ForeignKey("usuarios.id"))
    creado_en = Column(DateTime, default=datetime.utcnow)

    activa = Column(Boolean, default=True)