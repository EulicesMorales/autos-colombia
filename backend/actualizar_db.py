from database import engine, Base, SessionLocal
from models import UsuarioSistema

# 1. Crear la tabla en la base de datos
print("Creando tabla de usuarios del sistema...")
Base.metadata.create_all(bind=engine)

# 2. Insertar el Administrador y el Operador por defecto
db = SessionLocal()
try:
    # Revisar si ya existe el admin
    if not db.query(UsuarioSistema).filter(UsuarioSistema.username == "admin").first():
        admin = UsuarioSistema(username="admin", password="admin123", rol="Administrador")
        operador = UsuarioSistema(username="operador", password="operador123", rol="Operador")
        db.add(admin)
        db.add(operador)
        db.commit()
        print("✅ Usuarios 'admin' y 'operador' creados.")
    else:
        print("✅ Los usuarios ya existían.")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()