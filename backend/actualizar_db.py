from database import SessionLocal
from models import Usuario, Vehiculo, Mensualidad
from datetime import date, timedelta
from config import TARIFAS_MENSUALES, DURACION_MENSUALIDAD_DIAS

def crear_datos():
    db = SessionLocal()
    
    # Lista de datos de prueba: (Nombre, Documento, Placa, Tipo)
    datos = [
        ("Carlos Andres Perez", "10203040", "ABC123", "Carro"),
        ("Maria Fernanda Gomez", "10987654", "XYZ987", "Carro"),
        ("Juan David Rodriguez", "10001000", "JDR456", "Carro"),
        ("Luisa Valentina Ortiz", "11223344", "MNO12D", "Moto"),
        ("Andres Felipe Castro", "55667788", "AFC34E", "Moto"),
        ("Diana Carolina Silva", "99887766", "DCS789", "Carro"),
        ("Jorge Enrique Mendoza", "10111213", "JEM01F", "Moto")
    ]

    print("⏳ Insertando datos de prueba...")
    
    for nombre, doc, placa, tipo in datos:
        # 1. Verificar si el usuario ya existe (por documento)
        usuario = db.query(Usuario).filter(Usuario.documento == doc).first()
        if not usuario:
            usuario = Usuario(
                tipo_documento="CC", 
                documento=doc, 
                nombre=nombre, 
                telefono="3001234567", 
                email=f"{nombre.split()[0].lower()}@correo.com",
                estado="Activo"
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)

        # 2. Verificar si el vehículo ya existe (por placa)
        vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa).first()
        if not vehiculo:
            vehiculo = Vehiculo(
                placa=placa, 
                tipo=tipo, 
                usuario_id=usuario.id
            )
            db.add(vehiculo)
            db.commit()
            db.refresh(vehiculo)

        # 3. Crear la mensualidad
        mensualidad_existente = db.query(Mensualidad).filter(Mensualidad.vehiculo_id == vehiculo.id).first()
        if not mensualidad_existente:
            hoy = date.today()
            mensualidad = Mensualidad(
                usuario_id=usuario.id,
                vehiculo_id=vehiculo.id,
                fecha_inicio=hoy,
                fecha_fin=hoy + timedelta(days=DURACION_MENSUALIDAD_DIAS),
                valor_mensual=TARIFAS_MENSUALES[tipo], # Aquí usa los $250.000 o $100.000
                estado="Vigente"
            )
            db.add(mensualidad)
            db.commit()
            print(f"✅ Creado: {nombre} - Placa: {placa} - Mensualidad: ${TARIFAS_MENSUALES[tipo]}")

    db.close()
    print("🎉 ¡Todos los datos de prueba han sido creados exitosamente!")

if __name__ == "__main__":
    crear_datos()