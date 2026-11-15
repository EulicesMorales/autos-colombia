# 🏎️ Autos Colombia — Sistema de gestión de parqueadero (por mensualidad)

Sistema web para el parqueadero **Autos Colombia**, que presta el servicio **por mensualidad**.
Gestiona usuarios mensualistas, celdas y la entrada/salida de vehículos.

| Iteración | Alcance |
|---|---|
| 1 | Gestión de entrada y salida de vehículos |
| 2 | Gestión de usuarios y de celdas **+ correcciones** a la Iteración 1 |

## 🧱 Stack
- **Frontend:** Angular 22 (standalone) · **Backend:** FastAPI + SQLAlchemy · **BD:** PostgreSQL

## ✅ Cambios de la Iteración 2 (correcciones al feedback)
| Hallazgo | Corrección |
|---|---|
| Cobro por hora | Eliminado. El servicio es por **mensualidad** (tablas `usuarios`, `vehiculos`, `mensualidades`). La salida ya no cobra. Solo ingresan vehículos con mensualidad **vigente** |
| Ingresos duplicados | Se rechaza (409) y además hay índice único parcial `uq_registro_placa_activo` en la BD |
| Validar placa y tipo | Formato colombiano: carro `ABC123`, moto `ABC12D`; tipo `Carro`/`Moto`; coherencia placa↔tipo. Valida en frontend y backend |
| Concurrencia en celdas | `SELECT … FOR UPDATE SKIP LOCKED` + índice único parcial `uq_registro_celda_activa` + reintento |
| Liberación masiva | Se **eliminó** `GET /reset-celdas`. La salida libera solo la celda de esa estancia. Al iniciar, el sistema repara celdas inconsistentes sin tocar las que tienen vehículo |
| Consulta de estancias finalizadas | `GET /estancias?estado=finalizadas` (placa, entrada, salida, duración, celda) + pestaña «Consultar estancias» (RF-06 / HU-02) |
| Mockups con rechazo | Estados de rechazo visibles en la interfaz (modal de rechazo) |

Funcionalidad retirada: `GET /reset-celdas` (peligrosa) y `POST /crear-celda/{numero}` (reemplazada por `POST /celdas`, con validaciones).

## 🚀 Instalación y ejecución

### Requisitos
Node.js 18+ · Python 3.9+ · PostgreSQL en el puerto 5432 con una BD llamada `autos_colombia`.

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

# Variables de entorno (opcionales; estos son los valores por defecto)
#   DATABASE_URL = postgresql+psycopg2://postgres:admin@localhost/autos_colombia
#   CORS_ORIGINS = http://localhost:4200,http://127.0.0.1:4200

uvicorn main:app --reload
```
Al iniciar, el backend **migra automáticamente** una BD de la Iteración 1 (no borra datos).
Documentación interactiva: http://127.0.0.1:8000/docs

Datos de prueba (opcional): `python datos_demo.py`

### Frontend
```bash
cd frontend
npm install
npm start          # http://localhost:4200
```

### Pruebas automáticas (backend)
```bash
cd backend
python -m unittest discover -s tests -v
```

## 🔌 Endpoints principales
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/entrada` | Registra ingreso (valida placa, tipo, duplicado, mensualidad y asigna celda) |
| PUT | `/salida/{placa}` | Registra salida y libera **solo** su celda |
| GET | `/vehiculos` | Vehículos dentro del parqueadero |
| GET | `/estancias?estado=activas\|finalizadas\|todas&placa=&desde=&hasta=` | Consulta de estancias |
| POST/GET | `/usuarios` | Crear / listar (`?buscar=`) usuarios |
| GET/PUT | `/usuarios/{id}` · `/usuarios/{id}/estado` | Detalle · actualizar · activar/desactivar |
| POST | `/usuarios/{id}/vehiculos` | Asociar vehículo |
| POST/GET | `/mensualidades` · PUT `/mensualidades/{id}/cancelar` | Mensualidades |
| GET/POST | `/celdas` · GET `/celdas/resumen` | Mapa de celdas · crear celda |
| PUT | `/celdas/{id}/estado` | Disponible ⇄ Mantenimiento (no permite sobre celdas ocupadas) |

Valores de ejemplo: mensualidad Carro $180.000 · Moto $90.000 · 30 días (`backend/config.py`).
Celdas: 50 (A-1…A-40 carros, A-41…A-50 motos).

## 🗂️ Estructura del backend
```
backend/
├── main.py            # app, CORS, manejo de errores, arranque
├── config.py          # reglas de negocio y entorno
├── routers/           # capa HTTP
├── servicios/         # reglas de negocio
├── repositorios.py    # consultas y bloqueos de fila
├── validadores.py     # placas, tipos, usuarios
├── models.py · schemas.py · migraciones.py
└── tests/             # pruebas automáticas
```

*Desarrollado para la asignatura de Ingeniería de Software — IU Digital de Antioquia.*
