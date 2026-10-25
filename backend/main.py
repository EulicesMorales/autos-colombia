from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models, schemas
from datetime import datetime, timezone
import math

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────────────────────────────────
# SEED MEJORADO: Asegura que existan las 50 celdas
# ─────────────────────────────────────────────────────────
@app.on_event("startup")
def seed_celdas():
    db = SessionLocal()
    try:
        total_actual = db.query(models.Celda).count()
        if total_actual < 50:
            faltantes = 50 - total_actual
            print(f"⚠️ Faltan celdas. Creando {faltantes} celdas...")
            for i in range(total_actual + 1, 51):
                db.add(models.Celda(numero=f"A-{i}", estado="Disponible"))
            db.commit()
            print("✅ 50 celdas aseguradas en la BD.")
        else:
            print("ℹ️ Ya hay 50 o más celdas en la BD.")
    finally:
        db.close()

# ─────────────────────────────────────────────────────────
# RUTA DE EMERGENCIA: Para liberar todas las celdas de golpe
# ─────────────────────────────────────────────────────────
@app.get("/reset-celdas")
def reset_celdas(db: Session = Depends(get_db)):
    celdas = db.query(models.Celda).all()
    for c in celdas:
        c.estado = "Disponible"
    db.commit()
    return {"mensaje": f"Se resetearon {len(celdas)} celdas a Disponible"}

@app.post("/crear-celda/{numero}")
def crear_celda(numero: str, db: Session = Depends(get_db)):
    nueva_celda = models.Celda(numero=numero)
    db.add(nueva_celda)
    db.commit()
    return {"mensaje": f"Celda {numero} creada"}

@app.post("/entrada", response_model=schemas.RegistroRespuesta)
def registrar_entrada(registro: schemas.RegistroCrear, db: Session = Depends(get_db)):
    celda = db.query(models.Celda).filter(models.Celda.estado == "Disponible").first()
    if not celda:
        raise HTTPException(status_code=400, detail="No hay celdas disponibles")

    nuevo_registro = models.Registro(
        placa=registro.placa,
        tipo_vehiculo=registro.tipo_vehiculo,
        celda_id=celda.id
    )
    celda.estado = "Ocupada"

    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro

@app.put("/salida/{placa}")
def registrar_salida(placa: str, db: Session = Depends(get_db)):
    registro = db.query(models.Registro).filter(
        models.Registro.placa == placa,
        models.Registro.hora_salida == None
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado o ya salió")

    # 1. Registrar hora de salida
    registro.hora_salida = datetime.now(timezone.utc)
    
    # 2. Calcular tiempo parqueado
    tiempo_parqueado = registro.hora_salida - registro.hora_entrada
    minutos_totales = tiempo_parqueado.total_seconds() / 60
    
    # Cobramos por hora o fracción (mínimo 1 hora)
    horas_cobrar = math.ceil(minutos_totales / 60)
    if horas_cobrar == 0:
        horas_cobrar = 1 
        
    # 3. Calcular tarifa (Puedes cambiar estos precios si quieres)
    tarifa_hora = 5000 if registro.tipo_vehiculo == "Carro" else 3000
    total_pagar = horas_cobrar * tarifa_hora

    # 4. Liberar la celda
    celda = db.query(models.Celda).filter(models.Celda.id == registro.celda_id).first()
    if celda:
        celda.estado = "Disponible"

    db.commit()
    
    # 5. Devolver el mensaje exacto con el cobro
    return {
        "mensaje": f"Vehículo {placa} debe ${total_pagar:,.0f} por {horas_cobrar} hora(s) de parqueo."
    }
    
    
@app.get("/vehiculos", response_model=list[schemas.RegistroRespuesta])
def listar_vehiculos(db: Session = Depends(get_db)):
    registros = (
        db.query(models.Registro)
        .filter(models.Registro.hora_salida == None)
        .order_by(models.Registro.hora_entrada.desc())
        .all()
    )
    return registros