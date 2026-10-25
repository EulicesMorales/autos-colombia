from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Celda(Base):
    __tablename__ = "celdas"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True)
    estado = Column(String, default="Disponible") # Puede ser "Disponible" u "Ocupada"

class Registro(Base):
    __tablename__ = "registros"
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, index=True)
    tipo_vehiculo = Column(String) # "Carro" o "Moto"
    hora_entrada = Column(DateTime(timezone=True), server_default=func.now())
    hora_salida = Column(DateTime(timezone=True), nullable=True)
    celda_id = Column(Integer, ForeignKey("celdas.id"))