from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import config
import models
from database import engine, SessionLocal
from errores import ErrorNegocio
from migraciones import migrar, sincronizar_celdas, asegurar_celdas
from routers import estancias, usuarios, mensualidades, celdas


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)   # tablas nuevas
    migrar(engine)                                  # columnas / índices de la Iteración 2
    asegurar_celdas(SessionLocal)                   # 50 celdas
    sincronizar_celdas(engine)                      # repara estados inconsistentes
    yield


app = FastAPI(title="Autos Colombia - API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGENES_PERMITIDOS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ErrorNegocio)
async def manejar_error_negocio(_: Request, exc: ErrorNegocio):
    # `detail` siempre es un texto legible para mostrar en la interfaz.
    return JSONResponse(status_code=exc.status_code,
                        content={"detail": exc.mensaje, "codigo": exc.codigo})


@app.exception_handler(RequestValidationError)
async def manejar_validacion(_: Request, exc: RequestValidationError):
    e = exc.errors()[0] if exc.errors() else {}
    campo = (e.get("loc") or ["dato"])[-1]
    return JSONResponse(status_code=422,
                        content={"detail": f"Dato inválido o faltante: '{campo}'.", "codigo": "DATO_INVALIDO"})


@app.get("/salud", tags=["Sistema"])
def salud():
    return {"estado": "activo"}


app.include_router(estancias.router)
app.include_router(usuarios.router)
app.include_router(mensualidades.router)
app.include_router(celdas.router)
