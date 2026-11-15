"""Carga datos de demostración (opcional): 3 usuarios con vehículos y mensualidades,
más 1 usuario SIN mensualidad para probar el rechazo.
Uso (desde /backend):  python datos_demo.py"""
import models
from database import engine, SessionLocal
from migraciones import migrar, asegurar_celdas, sincronizar_celdas
from errores import ErrorNegocio
from servicios import usuarios as usr, mensualidades as men

models.Base.metadata.create_all(bind=engine)
migrar(engine)
asegurar_celdas(SessionLocal)
sincronizar_celdas(engine)

DEMO = [
    ("CC", "1001001001", "Andrés Jaramillo", [("ABC123", "Carro")], True),
    ("CC", "1002002002", "Karen Vergara", [("XYZ12A", "Moto")], True),
    ("CC", "1003003003", "Eulices Morales", [("DEF456", "Carro")], True),
    ("CC", "1004004004", "Cliente Sin Mensualidad", [("GHI789", "Carro")], False),
]
db = SessionLocal()
try:
    for td, doc, nombre, vehs, con_mens in DEMO:
        try:
            u = usr.crear_usuario(db, td, doc, nombre, "3001234567")
        except ErrorNegocio as e:
            print(f"· {nombre}: {e.mensaje}")
            continue
        for placa, tipo in vehs:
            usr.agregar_vehiculo(db, u["id"], placa, tipo)
            if con_mens:
                men.crear_mensualidad(db, u["id"], placa)
        print(f"✔ {nombre} creado ({', '.join(p for p, _ in vehs)}) {'con' if con_mens else 'SIN'} mensualidad")
finally:
    db.close()
