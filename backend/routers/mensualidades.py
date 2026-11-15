from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import schemas
from servicios import mensualidades as srv

router = APIRouter(prefix="/mensualidades", tags=["Mensualidades"])


@router.post("", response_model=schemas.MensualidadRespuesta, status_code=201)
def crear_mensualidad(datos: schemas.MensualidadCrear, db: Session = Depends(get_db)):
    return srv.crear_mensualidad(db, datos.usuario_id, datos.placa)


@router.get("", response_model=List[schemas.MensualidadRespuesta])
def listar_mensualidades(usuario_id: Optional[int] = None, db: Session = Depends(get_db)):
    return srv.listar_mensualidades(db, usuario_id)


@router.put("/{mensualidad_id}/cancelar", response_model=schemas.MensualidadRespuesta)
def cancelar_mensualidad(mensualidad_id: int, db: Session = Depends(get_db)):
    return srv.cancelar_mensualidad(db, mensualidad_id)
