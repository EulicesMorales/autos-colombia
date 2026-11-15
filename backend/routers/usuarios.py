from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import schemas
from servicios import usuarios as srv

router = APIRouter(prefix="/usuarios", tags=["Gestión de usuarios"])


@router.post("", response_model=schemas.UsuarioRespuesta, status_code=201)
def crear_usuario(datos: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    return srv.crear_usuario(db, datos.tipo_documento, datos.documento, datos.nombre,
                             datos.telefono, datos.email)


@router.get("", response_model=List[schemas.UsuarioRespuesta])
def listar_usuarios(buscar: Optional[str] = None, db: Session = Depends(get_db)):
    return srv.listar_usuarios(db, buscar)


@router.get("/{usuario_id}", response_model=schemas.UsuarioRespuesta)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return srv.obtener_usuario(db, usuario_id)


@router.put("/{usuario_id}", response_model=schemas.UsuarioRespuesta)
def actualizar_usuario(usuario_id: int, datos: schemas.UsuarioActualizar, db: Session = Depends(get_db)):
    return srv.actualizar_usuario(db, usuario_id, datos.nombre, datos.telefono, datos.email)


@router.put("/{usuario_id}/estado", response_model=schemas.UsuarioRespuesta)
def cambiar_estado(usuario_id: int, datos: schemas.EstadoCambiar, db: Session = Depends(get_db)):
    return srv.cambiar_estado_usuario(db, usuario_id, datos.estado)


@router.post("/{usuario_id}/vehiculos", response_model=schemas.UsuarioRespuesta, status_code=201)
def agregar_vehiculo(usuario_id: int, datos: schemas.VehiculoCrear, db: Session = Depends(get_db)):
    return srv.agregar_vehiculo(db, usuario_id, datos.placa, datos.tipo_vehiculo)
