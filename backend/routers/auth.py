from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas, models

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=schemas.LoginResponse)
def login(datos: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Buscar el usuario en la base de datos
    user = db.query(models.UsuarioSistema).filter(models.UsuarioSistema.username == datos.username).first()
    
    # Validar credenciales
    if not user or user.password != datos.password:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    
    return {"mensaje": "Login exitoso", "rol": user.rol}

# Un endpoint extra para que puedas crear nuevos usuarios del sistema (opcional)
@router.post("/crear-usuario", response_model=schemas.LoginResponse)
def crear_usuario(datos: schemas.UsuarioSistemaCrear, db: Session = Depends(get_db)):
    nuevo = models.UsuarioSistema(username=datos.username, password=datos.password, rol=datos.rol)
    db.add(nuevo)
    db.commit()
    return {"mensaje": "Usuario del sistema creado", "rol": nuevo.rol}