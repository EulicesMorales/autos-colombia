"""Gestión de celdas."""
from sqlalchemy.exc import IntegrityError
from errores import ErrorNegocio
from validadores import validar_numero_celda, normalizar_tipo
from repositorios import RepositorioCeldas
from models import Celda


def celda_a_dict(c: Celda, placa=None) -> dict:
    return {"id": c.id, "numero": c.numero, "tipo": c.tipo, "estado": c.estado, "placa": placa}


def listar_celdas(db) -> list:
    return [celda_a_dict(c, placa) for c, placa in RepositorioCeldas.listar_con_placa(db)]


def resumen_celdas(db) -> dict:
    celdas = db.query(Celda).all()
    r = {"total": len(celdas), "Disponible": 0, "Ocupada": 0, "Mantenimiento": 0}
    for c in celdas:
        r[c.estado] = r.get(c.estado, 0) + 1
    return r


def crear_celda(db, numero, tipo) -> dict:
    numero = validar_numero_celda(numero)
    tipo = normalizar_tipo(tipo)
    if db.query(Celda).filter(Celda.numero == numero).first():
        raise ErrorNegocio(409, "CELDA_DUPLICADA", f"Ya existe la celda {numero}.")
    c = Celda(numero=numero, tipo=tipo, estado="Disponible")
    db.add(c)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ErrorNegocio(409, "CELDA_DUPLICADA", f"Ya existe la celda {numero}.")
    db.refresh(c)
    return celda_a_dict(c)


def cambiar_estado_celda(db, celda_id, estado) -> dict:
    """Solo Disponible <-> Mantenimiento. 'Ocupada' únicamente la fija una entrada,
    y solo la libera la salida del vehículo que la ocupa."""
    if estado not in ("Disponible", "Mantenimiento"):
        raise ErrorNegocio(422, "ESTADO_INVALIDO",
                           "Solo se puede cambiar manualmente a Disponible o Mantenimiento.")
    c = RepositorioCeldas.por_id(db, celda_id, bloquear=True)
    if not c:
        db.rollback()
        raise ErrorNegocio(404, "CELDA_NO_ENCONTRADA", f"No existe la celda con id {celda_id}.")
    if c.estado == "Ocupada":
        db.rollback()
        raise ErrorNegocio(409, "CELDA_OCUPADA",
                           f"La celda {c.numero} tiene un vehículo dentro. Registra primero su salida.")
    c.estado = estado
    db.commit()
    db.refresh(c)
    return celda_a_dict(c)
