from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Observacion(Base):
    __tablename__ = "observaciones"

    id = Column(Integer, primary_key=True)

    # 🔥 nombre en BD = id_alumno, nombre en Python = id_alumno
    id_alumno = Column("id_alumno", Integer, ForeignKey("alumnos.id"))

    alumno = relationship("Alumno", back_populates="observaciones")

    comentario = Column(Text, nullable=False)

    id_creado_por = Column("creado_por", Integer, ForeignKey("usuarios.id"))
    creado_en = Column(DateTime, default=datetime.utcnow)

    activa = Column(Boolean, default=True)