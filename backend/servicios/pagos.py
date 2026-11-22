"""Servicio para registrar los pagos de las mensualidades."""
from sqlalchemy.orm import Session
from errores import ErrorNegocio
from models import Pago, Mensualidad
from datetime import datetime

def registrar_pago(db: Session, mensualidad_id: int, metodo_pago: str, banco: str = "Bancolombia"):
    mensualidad = db.query(Mensualidad).filter(Mensualidad.id == mensualidad_id).first()
    if not mensualidad:
        raise ErrorNegocio(404, "MENSUALIDAD_NO_ENCONTRADA", "La mensualidad no existe.")
    
    if mensualidad.estado == "Cancelada":
        raise ErrorNegocio(400, "MENSUALIDAD_CANCELADA", "No se puede pagar una mensualidad cancelada.")

    # Limpiamos el texto
    banco_limpio = str(banco).strip().title() if banco else "No aplica"
    
    # Si es transferencia, SOLO aceptamos Bancolombia
    if metodo_pago == "Transferencia" and banco_limpio != "Bancolombia":
        raise ErrorNegocio(400, "BANCO_INVALIDO", f"Banco erróneo ('{banco_limpio}'). Solo se aceptan transferencias de Bancolombia.")

    # Si es efectivo, guardamos 'No aplica' en la base de datos
    if metodo_pago == "Efectivo":
        banco_limpio = "No aplica"

    print(f"--> PAGO PROCESADO: Metodo='{metodo_pago}', Banco='{banco_limpio}'")

    nuevo_pago = Pago(
        mensualidad_id=mensualidad.id,
        monto=mensualidad.valor_mensual,
        metodo_pago=metodo_pago,
        banco=banco_limpio,
        referencia=f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    
    return nuevo_pago

def listar_pagos(db: Session):
    return db.query(Pago).order_by(Pago.id.desc()).all()