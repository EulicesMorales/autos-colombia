from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import schemas
from servicios import celdas as srv

router = APIRouter(prefix="/celdas", tags=["Gestión de celdas"])


@router.get("", response_model=List[schemas.CeldaRespuesta])
def listar_celdas(db: Session = Depends(get_db)):
    return srv.listar_celdas(db)


@router.get("/resumen")
def resumen_celdas(db: Session = Depends(get_db)):
    return srv.resumen_celdas(db)


@router.post("", response_model=schemas.CeldaRespuesta, status_code=201)
def crear_celda(datos: schemas.CeldaCrear, db: Session = Depends(get_db)):
    return srv.crear_celda(db, datos.numero, datos.tipo)


@router.put("/{celda_id}/estado", response_model=schemas.CeldaRespuesta)
def cambiar_estado(celda_id: int, datos: schemas.EstadoCambiar, db: Session = Depends(get_db)):
    return srv.cambiar_estado_celda(db, celda_id, datos.estado)
