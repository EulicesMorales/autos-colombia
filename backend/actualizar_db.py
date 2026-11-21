from database import engine, Base
from models import Pago  # Importante: importar el modelo para que SQLAlchemy lo "vea"
from sqlalchemy import text

print("Conectando a la base de datos...")
try:
    # 1. Crear la tabla 'pagos' si no existe
    Base.metadata.create_all(bind=engine)
    print("✅ Tabla 'pagos' creada o ya existente.")

    # 2. Ahora que la tabla existe, agregar la columna 'banco'
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE pagos ADD COLUMN IF NOT EXISTS banco VARCHAR(50);"))
        conn.commit()
        print("✅ ¡Columna 'banco' agregada exitosamente a la tabla 'pagos'!")
        
except Exception as e:
    print(f"❌ Error al actualizar la base de datos: {e}")