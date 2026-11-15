from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
import schemas
from servicios import estancias as srv

router = APIRouter(tags=["Entrada y salida de vehículos"])


@router.post("/entrada", response_model=schemas.RegistroRespuesta)
def registrar_entrada(datos: schemas.RegistroCrear, db: Session = Depends(get_db)):
    return srv.registrar_entrada(db, datos.placa, datos.tipo_vehiculo)


@router.put("/salida/{placa}", response_model=schemas.SalidaRespuesta)
def registrar_salida(placa: str, db: Session = Depends(get_db)):
    return srv.registrar_salida(db, placa)


@router.get("/vehiculos", response_model=List[schemas.RegistroRespuesta])
def listar_vehiculos(db: Session = Depends(get_db)):
    """Vehículos actualmente dentro del parqueadero (compatibilidad Iteración 1)."""
    return srv.listar_estancias(db, "activas")


@router.get("/estancias", response_model=List[schemas.RegistroRespuesta])
def consultar_estancias(
    estado: str = Query("activas", description="activas | finalizadas | todas"),
    placa: Optional[str] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    limite: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Consulta de estancias (RF-06 / HU-02): placa, entrada, salida, duración y celda."""
    return srv.listar_estancias(db, estado, placa, desde, hasta, limite)
