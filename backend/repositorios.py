"""Capa de acceso a datos. Aquí viven las consultas y los bloqueos de fila."""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import func
from config import ZONA_COLOMBIA
from models import Usuario, Vehiculo, Mensualidad, Celda, Registro


class RepositorioEstancias:
    @staticmethod
    def activa_por_placa(db, placa: str, bloquear: bool = False) -> Optional[Registro]:
        q = db.query(Registro).filter(Registro.placa == placa, Registro.hora_salida.is_(None))
        if bloquear:
            q = q.with_for_update()
        return q.first()

    @staticmethod
    def listar(db, estado="activas", placa=None, desde=None, hasta=None, limite=200):
        q = db.query(Registro, Celda.numero).outerjoin(Celda, Celda.id == Registro.celda_id)
        if estado == "activas":
            q = q.filter(Registro.hora_salida.is_(None)).order_by(Registro.hora_entrada.desc())
        elif estado == "finalizadas":
            q = q.filter(Registro.hora_salida.isnot(None)).order_by(Registro.hora_salida.desc())
        else:
            q = q.order_by(Registro.hora_entrada.desc())
        if placa:
            q = q.filter(Registro.placa == placa)
        if desde:
            q = q.filter(Registro.hora_entrada >= datetime(desde.year, desde.month, desde.day, tzinfo=ZONA_COLOMBIA))
        if hasta:
            fin = datetime(hasta.year, hasta.month, hasta.day, tzinfo=ZONA_COLOMBIA) + timedelta(days=1)
            q = q.filter(Registro.hora_entrada < fin)
        return q.limit(limite).all()


class RepositorioCeldas:
    @staticmethod
    def siguiente_disponible(db, tipo: str) -> Optional[Celda]:
        """Primera celda libre del tipo pedido. FOR UPDATE SKIP LOCKED (PostgreSQL):
        dos solicitudes simultáneas nunca reciben la misma celda."""
        return (
            db.query(Celda)
            .filter(Celda.estado == "Disponible", Celda.tipo == tipo)
            .order_by(Celda.id)
            .with_for_update(skip_locked=True)
            .first()
        )

    @staticmethod
    def por_id(db, celda_id: int, bloquear: bool = False) -> Optional[Celda]:
        q = db.query(Celda).filter(Celda.id == celda_id)
        if bloquear:
            q = q.with_for_update()
        return q.first()

    @staticmethod
    def listar_con_placa(db):
        return (
            db.query(Celda, Registro.placa)
            .outerjoin(Registro, (Registro.celda_id == Celda.id) & (Registro.hora_salida.is_(None)))
            .order_by(Celda.id)
            .all()
        )


class RepositorioUsuarios:
    @staticmethod
    def por_id(db, usuario_id: int) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()

    @staticmethod
    def por_documento(db, documento: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.documento == documento).first()

    @staticmethod
    def vehiculo_por_placa(db, placa: str) -> Optional[Vehiculo]:
        return db.query(Vehiculo).filter(Vehiculo.placa == placa).first()


class RepositorioMensualidades:
    @staticmethod
    def vigente_por_vehiculo(db, vehiculo_id: int, hoy) -> Optional[Mensualidad]:
        return (
            db.query(Mensualidad)
            .filter(Mensualidad.vehiculo_id == vehiculo_id,
                    Mensualidad.estado == "Vigente",
                    Mensualidad.fecha_inicio <= hoy,
                    Mensualidad.fecha_fin >= hoy)
            .order_by(Mensualidad.fecha_fin.desc())
            .first()
        )
