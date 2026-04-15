from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.database import Base
from datetime import datetime

class Historial(Base):
    __tablename__ = "historial"

    id = Column(Integer, primary_key=True)

    id_usuario = Column(Integer)
    correo = Column(String(120))
    tipo_usuario = Column(String(30))

    accion = Column(String(60))
    id_alumno = Column(Integer)

    detalle = Column(JSON)
    ip_origen = Column(String(45))

    registrado_en = Column(DateTime, default=datetime.utcnow)