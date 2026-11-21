"""Servicio para registrar los pagos de las mensualidades."""
from sqlalchemy.orm import Session
from errores import ErrorNegocio
from models import Pago, Mensualidad
from datetime import datetime

def registrar_pago(db: Session, mensualidad_id: int, metodo_pago: str, banco: str = "Bancolombia"):
    # 1. Verificar que la mensualidad exista
    mensualidad = db.query(Mensualidad).filter(Mensualidad.id == mensualidad_id).first()
    if not mensualidad:
        raise ErrorNegocio(404, "MENSUALIDAD_NO_ENCONTRADA", "La mensualidad no existe.")
    
    # 2. Verificar que no esté cancelada
    if mensualidad.estado == "Cancelada":
        raise ErrorNegocio(400, "MENSUALIDAD_CANCELADA", "No se puede pagar una mensualidad cancelada.")

    # 3. Registrar el pago
    nuevo_pago = Pago(
        mensualidad_id=mensualidad.id,
        monto=mensualidad.valor_mensual,
        metodo_pago=metodo_pago,
        banco=banco,
        referencia=f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    
    return nuevo_pago

def listar_pagos(db: Session):
    return db.query(Pago).order_by(Pago.id.desc()).all()