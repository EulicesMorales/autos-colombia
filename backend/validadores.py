"""Validaciones de entrada (puras, sin dependencias de FastAPI)."""
import re
from errores import ErrorNegocio
from config import TIPOS_VEHICULO

# Formato colombiano: carro ABC123 · moto ABC12D
RE_PLACA_CARRO = re.compile(r"^[A-Z]{3}\d{3}$")
RE_PLACA_MOTO = re.compile(r"^[A-Z]{3}\d{2}[A-Z]$")
RE_DOCUMENTO = re.compile(r"^[A-Za-z0-9]{5,15}$")
RE_TELEFONO = re.compile(r"^\d{7,10}$")
RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
RE_NUMERO_CELDA = re.compile(r"^[A-Z]{1,2}-\d{1,3}$")
TIPOS_DOCUMENTO = ("CC", "CE", "PAS", "NIT")


def normalizar_placa(placa) -> str:
    """'abc-123' / ' ABC 123 ' -> 'ABC123'"""
    return re.sub(r"[\s\-]", "", (placa or "")).upper()


def normalizar_tipo(tipo) -> str:
    t = (tipo or "").strip().capitalize()
    if t not in TIPOS_VEHICULO:
        raise ErrorNegocio(422, "TIPO_INVALIDO",
                           "Tipo de vehículo inválido. Solo se aceptan: Carro o Moto.")
    return t


def validar_placa(placa) -> str:
    p = normalizar_placa(placa)
    if not p:
        raise ErrorNegocio(422, "PLACA_INVALIDA", "Debes ingresar la placa del vehículo.")
    if not (RE_PLACA_CARRO.match(p) or RE_PLACA_MOTO.match(p)):
        raise ErrorNegocio(422, "PLACA_INVALIDA",
                           f"La placa '{p}' no tiene un formato válido. "
                           "Carro: ABC123 · Moto: ABC12D.")
    return p


def validar_placa_y_tipo(placa, tipo):
    """Valida formato de placa, tipo de vehículo y que ambos sean coherentes."""
    p = validar_placa(placa)
    t = normalizar_tipo(tipo)
    if t == "Carro" and not RE_PLACA_CARRO.match(p):
        raise ErrorNegocio(422, "PLACA_TIPO_INCOHERENTE",
                           f"La placa {p} tiene formato de moto, pero el tipo es Carro.")
    if t == "Moto" and not RE_PLACA_MOTO.match(p):
        raise ErrorNegocio(422, "PLACA_TIPO_INCOHERENTE",
                           f"La placa {p} tiene formato de carro, pero el tipo es Moto.")
    return p, t


def validar_usuario(tipo_documento, documento, nombre, telefono=None, email=None):
    td = (tipo_documento or "").strip().upper()
    if td not in TIPOS_DOCUMENTO:
        raise ErrorNegocio(422, "DOCUMENTO_INVALIDO",
                           f"Tipo de documento inválido. Use: {', '.join(TIPOS_DOCUMENTO)}.")
    doc = (documento or "").strip()
    if not RE_DOCUMENTO.match(doc):
        raise ErrorNegocio(422, "DOCUMENTO_INVALIDO",
                           "El documento debe tener entre 5 y 15 caracteres alfanuméricos.")
    nom = " ".join((nombre or "").split())
    if len(nom) < 3 or len(nom) > 100:
        raise ErrorNegocio(422, "NOMBRE_INVALIDO", "El nombre debe tener entre 3 y 100 caracteres.")
    tel = (telefono or "").strip() or None
    if tel and not RE_TELEFONO.match(tel):
        raise ErrorNegocio(422, "TELEFONO_INVALIDO", "El teléfono debe tener entre 7 y 10 dígitos.")
    mail = (email or "").strip().lower() or None
    if mail and not RE_EMAIL.match(mail):
        raise ErrorNegocio(422, "EMAIL_INVALIDO", "El correo electrónico no es válido.")
    return td, doc.upper(), nom, tel, mail


def validar_numero_celda(numero) -> str:
    n = (numero or "").strip().upper()
    if not RE_NUMERO_CELDA.match(n):
        raise ErrorNegocio(422, "CELDA_INVALIDA",
                           "El número de celda debe tener el formato A-1 (letras, guion y número).")
    return n
