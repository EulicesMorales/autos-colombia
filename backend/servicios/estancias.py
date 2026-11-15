"""Gestión de entrada y salida de vehículos (Iteración 1, corregida)."""
from sqlalchemy.exc import IntegrityError
from errores import ErrorNegocio
from validadores import validar_placa_y_tipo, validar_placa
from repositorios import (RepositorioEstancias, RepositorioCeldas,
                          RepositorioUsuarios, RepositorioMensualidades)
from models import Registro
from servicios.utilidades import ahora, hoy, duracion_minutos, duracion_texto

MAX_REINTENTOS = 5


def estancia_a_dict(registro: Registro, celda_numero=None) -> dict:
    mins = duracion_minutos(registro.hora_entrada, registro.hora_salida)
    return {
        "id": registro.id,
        "placa": registro.placa,
        "tipo_vehiculo": registro.tipo_vehiculo,
        "hora_entrada": registro.hora_entrada,
        "hora_salida": registro.hora_salida,
        "celda_id": registro.celda_id,
        "celda_numero": celda_numero,
        "duracion_minutos": mins,
        "duracion_texto": duracion_texto(mins),
    }


def registrar_entrada(db, placa, tipo_vehiculo) -> dict:
    # 1) Validar formato de placa, tipo y coherencia entre ambos
    placa, tipo = validar_placa_y_tipo(placa, tipo_vehiculo)

    # 2) Impedir ingreso duplicado
    if RepositorioEstancias.activa_por_placa(db, placa):
        raise ErrorNegocio(409, "PLACA_DUPLICADA",
                           f"El vehículo con placa {placa} ya se encuentra dentro del parqueadero.")

    # 3) Solo ingresan vehículos con mensualidad vigente
    vehiculo = RepositorioUsuarios.vehiculo_por_placa(db, placa)
    if not vehiculo:
        raise ErrorNegocio(403, "SIN_MENSUALIDAD",
                           f"La placa {placa} no está asociada a ningún usuario con mensualidad. "
                           "Solo ingresan vehículos con mensualidad vigente.")
    if vehiculo.tipo != tipo:
        raise ErrorNegocio(409, "TIPO_NO_COINCIDE",
                           f"La placa {placa} está registrada como {vehiculo.tipo}, no como {tipo}.")
    if vehiculo.usuario.estado != "Activo":
        raise ErrorNegocio(403, "USUARIO_INACTIVO",
                           f"El usuario titular de la placa {placa} está inactivo.")
    mensualidad = RepositorioMensualidades.vigente_por_vehiculo(db, vehiculo.id, hoy())
    if not mensualidad:
        raise ErrorNegocio(403, "SIN_MENSUALIDAD",
                           f"La placa {placa} no tiene una mensualidad vigente. "
                           "Solo ingresan vehículos con mensualidad vigente.")
    mensualidad_id = mensualidad.id

    # 4) Asignar celda de forma segura ante solicitudes concurrentes
    for _ in range(MAX_REINTENTOS):
        celda = RepositorioCeldas.siguiente_disponible(db, tipo)
        if not celda:
            raise ErrorNegocio(409, "CELDA_NO_DISPONIBLE",
                               f"No hay celdas disponibles para {tipo}.")
        celda_numero = celda.numero
        celda.estado = "Ocupada"
        registro = Registro(placa=placa, tipo_vehiculo=tipo, hora_entrada=ahora(),
                            celda_id=celda.id, mensualidad_id=mensualidad_id)
        db.add(registro)
        try:
            db.commit()
        except IntegrityError:
            # Otra solicitud ganó la carrera (misma placa o misma celda).
            db.rollback()
            if RepositorioEstancias.activa_por_placa(db, placa):
                raise ErrorNegocio(409, "PLACA_DUPLICADA",
                                   f"El vehículo con placa {placa} ya se encuentra dentro del parqueadero.")
            continue  # la celda fue tomada: se intenta con la siguiente
        db.refresh(registro)
        return estancia_a_dict(registro, celda_numero)

    raise ErrorNegocio(409, "CELDA_NO_DISPONIBLE",
                       "No fue posible asignar una celda por alta concurrencia. Intente de nuevo.")


def registrar_salida(db, placa) -> dict:
    placa = validar_placa(placa)

    registro = RepositorioEstancias.activa_por_placa(db, placa, bloquear=True)
    if not registro:
        db.rollback()
        raise ErrorNegocio(404, "SIN_ESTANCIA_ACTIVA",
                           f"El vehículo {placa} no se encuentra en el parqueadero o ya salió.")

    registro.hora_salida = ahora()

    # Se libera ÚNICAMENTE la celda de esta estancia (nunca otras).
    celda = RepositorioCeldas.por_id(db, registro.celda_id, bloquear=True)
    numero = celda.numero if celda else None
    if celda and celda.estado == "Ocupada":
        celda.estado = "Disponible"

    db.commit()
    db.refresh(registro)
    d = estancia_a_dict(registro, numero)
    d["mensaje"] = (f"Salida registrada para {placa}. Celda {numero} liberada. "
                    f"Permanencia: {d['duracion_texto']}. Servicio cubierto por mensualidad.")
    return d


def listar_estancias(db, estado="activas", placa=None, desde=None, hasta=None, limite=200):
    if estado not in ("activas", "finalizadas", "todas"):
        raise ErrorNegocio(422, "FILTRO_INVALIDO", "El estado debe ser: activas, finalizadas o todas.")
    placa_norm = None
    if placa and placa.strip():
        placa_norm = validar_placa(placa)
    filas = RepositorioEstancias.listar(db, estado, placa_norm, desde, hasta, limite)
    return [estancia_a_dict(r, numero) for r, numero in filas]
