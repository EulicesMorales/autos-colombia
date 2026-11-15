from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date


# ── Estancias (entrada / salida / consulta) ──────────────
class RegistroCrear(BaseModel):
    placa: str
    tipo_vehiculo: str


class RegistroRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    placa: str
    tipo_vehiculo: str
    hora_entrada: datetime
    hora_salida: Optional[datetime] = None
    celda_id: int
    celda_numero: Optional[str] = None
    duracion_minutos: Optional[int] = None
    duracion_texto: Optional[str] = None


class SalidaRespuesta(RegistroRespuesta):
    mensaje: str


# ── Usuarios ─────────────────────────────────────────────
class VehiculoCrear(BaseModel):
    placa: str
    tipo_vehiculo: str


class VehiculoRespuesta(BaseModel):
    id: int
    placa: str
    tipo: str


class UsuarioCrear(BaseModel):
    tipo_documento: str
    documento: str
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None


class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None


class EstadoCambiar(BaseModel):
    estado: str


class UsuarioRespuesta(BaseModel):
    id: int
    tipo_documento: str
    documento: str
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    estado: str
    vehiculos: List[VehiculoRespuesta] = []


# ── Mensualidades ────────────────────────────────────────
class MensualidadCrear(BaseModel):
    usuario_id: int
    placa: str


class MensualidadRespuesta(BaseModel):
    id: int
    usuario_id: int
    nombre_usuario: str
    placa: str
    tipo_vehiculo: str
    fecha_inicio: date
    fecha_fin: date
    valor_mensual: int
    estado: str
    dias_restantes: int


# ── Celdas ───────────────────────────────────────────────
class CeldaCrear(BaseModel):
    numero: str
    tipo: str


class CeldaRespuesta(BaseModel):
    id: int
    numero: str
    tipo: str
    estado: str
    placa: Optional[str] = None
