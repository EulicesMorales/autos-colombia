"""Migración idempotente de la Iteración 1 a la Iteración 2.

`create_all()` crea tablas nuevas pero NO modifica las existentes, por eso este
módulo agrega lo que falta sin borrar datos. Se puede ejecutar muchas veces.
"""
import re
from sqlalchemy import inspect, text
from config import TOTAL_CELDAS, CELDAS_CARRO


def _columnas(engine, tabla):
    return {c["name"] for c in inspect(engine).get_columns(tabla)}


def migrar(engine):
    cols_celdas = _columnas(engine, "celdas")      # se leen ANTES de abrir la transacción
    cols_registros = _columnas(engine, "registros")
    with engine.begin() as con:
        # 1) celdas.tipo  (A-1..A-40 Carro, A-41..A-50 Moto en la primera migración)
        if "tipo" not in cols_celdas:
            con.execute(text("ALTER TABLE celdas ADD COLUMN tipo VARCHAR(10) NOT NULL DEFAULT 'Carro'"))
            for c in con.execute(text("SELECT id, numero FROM celdas")).fetchall():
                m = re.match(r"^A-(\d+)$", c.numero or "")
                if m and int(m.group(1)) > CELDAS_CARRO:
                    con.execute(text("UPDATE celdas SET tipo='Moto' WHERE id=:i"), {"i": c.id})
            print("🛠️  Migración: columna celdas.tipo agregada.")

        # 2) registros.mensualidad_id
        if "mensualidad_id" not in cols_registros:
            con.execute(text("ALTER TABLE registros ADD COLUMN mensualidad_id INTEGER REFERENCES mensualidades(id)"))
            print("🛠️  Migración: columna registros.mensualidad_id agregada.")

        # 3) Normalizar placas históricas ('abc-123' -> 'ABC123')
        con.execute(text("UPDATE registros SET placa = UPPER(REPLACE(REPLACE(placa,'-',''),' ',''))"))

    # 4) Índices únicos parciales (duplicados y doble asignación de celda)
    for nombre, col in (("uq_registro_placa_activo", "placa"), ("uq_registro_celda_activa", "celda_id")):
        try:
            with engine.begin() as con:
                con.execute(text(f"CREATE UNIQUE INDEX IF NOT EXISTS {nombre} "
                                 f"ON registros({col}) WHERE hora_salida IS NULL"))
        except Exception as e:  # datos viejos con duplicados activos
            print(f"⚠️  No se pudo crear {nombre}: hay registros activos duplicados en la BD "
                  f"(error de la Iteración 1). Cierra los duplicados y reinicia. Detalle: {e.__class__.__name__}")


def sincronizar_celdas(engine):
    """Repara inconsistencias dejadas por la antigua ruta /reset-celdas:
    - celda 'Ocupada' sin estancia activa  -> 'Disponible'
    - celda 'Disponible' con estancia activa -> 'Ocupada'
    Nunca toca celdas en 'Mantenimiento'."""
    with engine.begin() as con:
        a = con.execute(text(
            "UPDATE celdas SET estado='Disponible' WHERE estado='Ocupada' AND NOT EXISTS "
            "(SELECT 1 FROM registros r WHERE r.celda_id = celdas.id AND r.hora_salida IS NULL)")).rowcount
        b = con.execute(text(
            "UPDATE celdas SET estado='Ocupada' WHERE estado='Disponible' AND EXISTS "
            "(SELECT 1 FROM registros r WHERE r.celda_id = celdas.id AND r.hora_salida IS NULL)")).rowcount
    if a or b:
        print(f"🛠️  Celdas sincronizadas: {a} liberadas (sin vehículo), {b} marcadas ocupadas (con vehículo).")


def asegurar_celdas(session_factory):
    """Garantiza las 50 celdas (A-1..A-40 Carro, A-41..A-50 Moto)."""
    from models import Celda
    db = session_factory()
    try:
        existentes = {c.numero for c in db.query(Celda).all()}
        nuevas = 0
        for i in range(1, TOTAL_CELDAS + 1):
            num = f"A-{i}"
            if num not in existentes:
                db.add(Celda(numero=num, tipo="Carro" if i <= CELDAS_CARRO else "Moto", estado="Disponible"))
                nuevas += 1
        if nuevas:
            db.commit()
            print(f"✅ Se crearon {nuevas} celdas. Total asegurado: {TOTAL_CELDAS}.")
    finally:
        db.close()
