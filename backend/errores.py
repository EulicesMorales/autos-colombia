class ErrorNegocio(Exception):
    """Rechazo controlado de una operación. El router lo traduce a HTTP."""

    def __init__(self, status_code: int, codigo: str, mensaje: str):
        super().__init__(mensaje)
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
