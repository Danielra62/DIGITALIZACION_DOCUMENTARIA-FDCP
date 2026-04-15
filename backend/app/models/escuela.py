from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Escuela(Base):
    __tablename__ = "escuelas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(80), unique=True, nullable=False)
    activa = Column(Boolean, default=True)