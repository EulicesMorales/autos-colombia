from datetime import datetime, timezone
from config import ZONA_COLOMBIA


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def hoy():
    """Fecha actual en Colombia."""
    return datetime.now(ZONA_COLOMBIA).date()


def a_utc(dt: datetime) -> datetime:
    """SQLite devuelve fechas sin zona; las tratamos como UTC."""
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def duracion_minutos(entrada: datetime, salida=None) -> int:
    fin = a_utc(salida) if salida else ahora()
    return max(0, int((fin - a_utc(entrada)).total_seconds() // 60))


def duracion_texto(minutos: int) -> str:
    h, m = divmod(minutos, 60)
    return f"{h} h {m} min" if h else f"{m} min"
