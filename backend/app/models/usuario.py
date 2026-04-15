from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    correo = Column(String(120), unique=True, nullable=False)
    nombre_display = Column(String(120), nullable=False)
    password_hash = Column(String(255), nullable=False)
    id_rol = Column(Integer, ForeignKey("roles.id"))
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    rol = relationship("Rol")