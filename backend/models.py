from sqlalchemy import (Column, Integer, String, DateTime, Date, Numeric,
                        ForeignKey, Index, text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Usuario(Base):
    """Cliente mensualista del parqueadero."""
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    tipo_documento = Column(String(5), nullable=False)       # CC, CE, PAS, NIT
    documento = Column(String(20), nullable=False, unique=True, index=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(15), nullable=True)
    email = Column(String(120), nullable=True)
    estado = Column(String(10), nullable=False, default="Activo")  # Activo / Inactivo
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    vehiculos = relationship("Vehiculo", back_populates="usuario", order_by="Vehiculo.id")


class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(6), nullable=False, unique=True, index=True)
    tipo = Column(String(10), nullable=False)                # Carro / Moto
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="vehiculos")


class Mensualidad(Base):
    __tablename__ = "mensualidades"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False, index=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    valor_mensual = Column(Numeric(12, 0), nullable=False)
    estado = Column(String(10), nullable=False, default="Vigente")  # Vigente / Cancelada
    usuario = relationship("Usuario")
    vehiculo = relationship("Vehiculo")


class Celda(Base):
    __tablename__ = "celdas"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True)
    tipo = Column(String(10), nullable=False, default="Carro", server_default="Carro")
    estado = Column(String, default="Disponible")  # Disponible / Ocupada / Mantenimiento


class Registro(Base):
    """Estancia: entrada y salida de un vehículo."""
    __tablename__ = "registros"
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, index=True)
    tipo_vehiculo = Column(String)  # "Carro" o "Moto"
    hora_entrada = Column(DateTime(timezone=True), server_default=func.now())
    hora_salida = Column(DateTime(timezone=True), nullable=True)
    celda_id = Column(Integer, ForeignKey("celdas.id"))
    mensualidad_id = Column(Integer, ForeignKey("mensualidades.id"), nullable=True)

    __table_args__ = (
        # Una placa NO puede tener dos estancias activas (ni una celda dos vehículos):
        # la base de datos es la última barrera ante solicitudes simultáneas.
        Index("uq_registro_placa_activo", "placa", unique=True,
              postgresql_where=text("hora_salida IS NULL"),
              sqlite_where=text("hora_salida IS NULL")),
        Index("uq_registro_celda_activa", "celda_id", unique=True,
              postgresql_where=text("hora_salida IS NULL"),
              sqlite_where=text("hora_salida IS NULL")),
    )
