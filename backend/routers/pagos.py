from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import schemas
from servicios import pagos as srv

router = APIRouter(prefix="/pagos", tags=["Pagos"])

@router.post("", response_model=schemas.PagoRespuesta, status_code=201)
def crear_pago(datos: schemas.PagoCrear, db: Session = Depends(get_db)):
    # Usamos argumentos con nombre para evitar que se crucen los datos
    return srv.registrar_pago(
        db=db, 
        mensualidad_id=datos.mensualidad_id, 
        metodo_pago=datos.metodo_pago, 
        banco=datos.banco
    )

@router.get("", response_model=List[schemas.PagoRespuesta])
def listar_pagos(db: Session = Depends(get_db)):
    return srv.listar_pagos(db)