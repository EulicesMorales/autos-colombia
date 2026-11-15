"""Gestión de usuarios (clientes mensualistas) y sus vehículos."""
from sqlalchemy.exc import IntegrityError
from errores import ErrorNegocio
from validadores import validar_usuario, validar_placa_y_tipo
from repositorios import RepositorioUsuarios
from models import Usuario, Vehiculo


def usuario_a_dict(u: Usuario) -> dict:
    return {
        "id": u.id, "tipo_documento": u.tipo_documento, "documento": u.documento,
        "nombre": u.nombre, "telefono": u.telefono, "email": u.email, "estado": u.estado,
        "vehiculos": [{"id": v.id, "placa": v.placa, "tipo": v.tipo} for v in u.vehiculos],
    }


def _obtener(db, usuario_id) -> Usuario:
    u = RepositorioUsuarios.por_id(db, usuario_id)
    if not u:
        raise ErrorNegocio(404, "USUARIO_NO_ENCONTRADO", f"No existe el usuario con id {usuario_id}.")
    return u


def crear_usuario(db, tipo_documento, documento, nombre, telefono=None, email=None) -> dict:
    td, doc, nom, tel, mail = validar_usuario(tipo_documento, documento, nombre, telefono, email)
    if RepositorioUsuarios.por_documento(db, doc):
        raise ErrorNegocio(409, "USUARIO_DUPLICADO", f"Ya existe un usuario con el documento {doc}.")
    u = Usuario(tipo_documento=td, documento=doc, nombre=nom, telefono=tel, email=mail, estado="Activo")
    db.add(u)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ErrorNegocio(409, "USUARIO_DUPLICADO", f"Ya existe un usuario con el documento {doc}.")
    db.refresh(u)
    return usuario_a_dict(u)


def listar_usuarios(db, buscar=None) -> list:
    q = db.query(Usuario).order_by(Usuario.id.desc())
    if buscar and buscar.strip():
        patron = f"%{buscar.strip()}%"
        q = q.filter((Usuario.nombre.ilike(patron)) | (Usuario.documento.ilike(patron)))
    return [usuario_a_dict(u) for u in q.all()]


def obtener_usuario(db, usuario_id) -> dict:
    return usuario_a_dict(_obtener(db, usuario_id))


def actualizar_usuario(db, usuario_id, nombre=None, telefono=None, email=None) -> dict:
    u = _obtener(db, usuario_id)
    _, _, nom, tel, mail = validar_usuario(u.tipo_documento, u.documento,
                                           nombre if nombre is not None else u.nombre,
                                           telefono if telefono is not None else u.telefono,
                                           email if email is not None else u.email)
    u.nombre, u.telefono, u.email = nom, tel, mail
    db.commit()
    db.refresh(u)
    return usuario_a_dict(u)


def cambiar_estado_usuario(db, usuario_id, estado) -> dict:
    if estado not in ("Activo", "Inactivo"):
        raise ErrorNegocio(422, "ESTADO_INVALIDO", "El estado debe ser Activo o Inactivo.")
    u = _obtener(db, usuario_id)
    u.estado = estado
    db.commit()
    db.refresh(u)
    return usuario_a_dict(u)


def agregar_vehiculo(db, usuario_id, placa, tipo) -> dict:
    u = _obtener(db, usuario_id)
    placa, tipo = validar_placa_y_tipo(placa, tipo)
    existente = RepositorioUsuarios.vehiculo_por_placa(db, placa)
    if existente:
        raise ErrorNegocio(409, "PLACA_REGISTRADA", f"La placa {placa} ya está registrada en el sistema.")
    db.add(Vehiculo(placa=placa, tipo=tipo, usuario_id=u.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ErrorNegocio(409, "PLACA_REGISTRADA", f"La placa {placa} ya está registrada en el sistema.")
    db.refresh(u)
    return usuario_a_dict(u)
