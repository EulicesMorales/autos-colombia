"""Mensualidades: habilitan el ingreso de un vehículo."""
from datetime import timedelta
from sqlalchemy.exc import IntegrityError
from errores import ErrorNegocio
from validadores import validar_placa
from config import TARIFAS_MENSUALES, DURACION_MENSUALIDAD_DIAS
from repositorios import RepositorioUsuarios, RepositorioMensualidades
from models import Mensualidad
from servicios.utilidades import hoy


def estado_actual(m: Mensualidad) -> str:
    if m.estado == "Cancelada":
        return "Cancelada"
    return "Vencida" if m.fecha_fin < hoy() else "Vigente"


def mensualidad_a_dict(m: Mensualidad) -> dict:
    est = estado_actual(m)
    return {
        "id": m.id, "usuario_id": m.usuario_id, "nombre_usuario": m.usuario.nombre,
        "placa": m.vehiculo.placa, "tipo_vehiculo": m.vehiculo.tipo,
        "fecha_inicio": m.fecha_inicio, "fecha_fin": m.fecha_fin,
        "valor_mensual": int(m.valor_mensual), "estado": est,
        "dias_restantes": max(0, (m.fecha_fin - hoy()).days) if est == "Vigente" else 0,
    }


def crear_mensualidad(db, usuario_id, placa) -> dict:
    usuario = RepositorioUsuarios.por_id(db, usuario_id)
    if not usuario:
        raise ErrorNegocio(404, "USUARIO_NO_ENCONTRADO", f"No existe el usuario con id {usuario_id}.")
    if usuario.estado != "Activo":
        raise ErrorNegocio(403, "USUARIO_INACTIVO", "No se puede crear una mensualidad a un usuario inactivo.")
    placa = validar_placa(placa)
    vehiculo = RepositorioUsuarios.vehiculo_por_placa(db, placa)
    if not vehiculo or vehiculo.usuario_id != usuario.id:
        raise ErrorNegocio(404, "VEHICULO_NO_ENCONTRADO",
                           f"La placa {placa} no está registrada para este usuario. Regístrala primero.")
    vigente = RepositorioMensualidades.vigente_por_vehiculo(db, vehiculo.id, hoy())
    if vigente:
        raise ErrorNegocio(409, "MENSUALIDAD_VIGENTE",
                           f"La placa {placa} ya tiene una mensualidad vigente hasta el {vigente.fecha_fin}.")
    inicio = hoy()
    m = Mensualidad(usuario_id=usuario.id, vehiculo_id=vehiculo.id, fecha_inicio=inicio,
                    fecha_fin=inicio + timedelta(days=DURACION_MENSUALIDAD_DIAS),
                    valor_mensual=TARIFAS_MENSUALES[vehiculo.tipo], estado="Vigente")
    db.add(m)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ErrorNegocio(409, "MENSUALIDAD_VIGENTE", "No se pudo crear la mensualidad. Intente de nuevo.")
    db.refresh(m)
    return mensualidad_a_dict(m)


def listar_mensualidades(db, usuario_id=None) -> list:
    q = db.query(Mensualidad).order_by(Mensualidad.id.desc())
    if usuario_id:
        q = q.filter(Mensualidad.usuario_id == usuario_id)
    return [mensualidad_a_dict(m) for m in q.all()]


def cancelar_mensualidad(db, mensualidad_id) -> dict:
    m = db.query(Mensualidad).filter(Mensualidad.id == mensualidad_id).first()
    if not m:
        raise ErrorNegocio(404, "MENSUALIDAD_NO_ENCONTRADA", f"No existe la mensualidad {mensualidad_id}.")
    m.estado = "Cancelada"
    db.commit()
    db.refresh(m)
    return mensualidad_a_dict(m)
