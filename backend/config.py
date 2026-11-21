"""Configuración central del sistema (reglas de negocio y entorno)."""
import os
from datetime import timezone, timedelta

# ── Entorno ──────────────────────────────────────────────
# Puede sobrescribirse con la variable de entorno DATABASE_URL (recomendado).
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:admin@localhost/autos_colombia",
)
ORIGENES_PERMITIDOS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200"
    ).split(",")
    if o.strip()
]

# ── Reglas de negocio: servicio por MENSUALIDAD ─────────
TARIFAS_MENSUALES = {"Carro": 250000, "Moto": 100000}  # valores de ejemplo (COP)
DURACION_MENSUALIDAD_DIAS = 30

TIPOS_VEHICULO = ("Carro", "Moto")
ESTADOS_CELDA = ("Disponible", "Ocupada", "Mantenimiento")

# 50 celdas: A-1..A-40 para carros y A-41..A-50 para motos
TOTAL_CELDAS = 50
CELDAS_CARRO = 40

# Hora de Colombia (UTC-5, sin horario de verano). Evita depender de tzdata en Windows.
ZONA_COLOMBIA = timezone(timedelta(hours=-5))
