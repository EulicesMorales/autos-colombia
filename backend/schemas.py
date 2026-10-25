from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RegistroCrear(BaseModel):
    placa: str
    tipo_vehiculo: str

class RegistroRespuesta(BaseModel):
    id: int
    placa: str
    tipo_vehiculo: str
    hora_entrada: datetime
    hora_salida: Optional[datetime] = None
    celda_id: int

    class Config:
        from_attributes = True