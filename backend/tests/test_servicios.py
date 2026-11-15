"""Pruebas de la capa de servicios (sin servidor). Ejecutar desde /backend:
    python -m unittest discover -s tests -v
Usan SQLite temporal; no tocan PostgreSQL."""
import os, sys, tempfile, threading, unittest

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import event, text            # noqa: E402
import database, models                        # noqa: E402
from database import engine, SessionLocal      # noqa: E402
from errores import ErrorNegocio               # noqa: E402
from migraciones import migrar, sincronizar_celdas, asegurar_celdas  # noqa: E402
from servicios import estancias as est, usuarios as usr, mensualidades as men, celdas as cel  # noqa: E402


@event.listens_for(engine, "connect")
def _sqlite_modo(dbapi_con, _):
    dbapi_con.isolation_level = None  # control manual de transacciones


@event.listens_for(engine, "begin")
def _sqlite_begin(con):
    con.exec_driver_sql("BEGIN IMMEDIATE")  # serializa escritores como lo haría FOR UPDATE


def reiniciar_bd():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    asegurar_celdas(SessionLocal)


def crear_cliente(db, doc="1001", placa="ABC123", tipo="Carro", con_mensualidad=True):
    u = usr.crear_usuario(db, "CC", doc.rjust(6, "0"), "Juan Pérez", "3001234567", "j@x.co")
    usr.agregar_vehiculo(db, u["id"], placa, tipo)
    if con_mensualidad:
        men.crear_mensualidad(db, u["id"], placa)
    return u


def rechazo(testcase, codigo, fn, *a, **k):
    with testcase.assertRaises(ErrorNegocio) as cm:
        fn(*a, **k)
    testcase.assertEqual(cm.exception.codigo, codigo, cm.exception.mensaje)
    return cm.exception


class Base(unittest.TestCase):
    def setUp(self):
        reiniciar_bd()
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()


class TestValidaciones(Base):
    def test_placas_validas_y_normalizacion(self):
        crear_cliente(self.db, "1", "ABC123", "Carro")
        r = est.registrar_entrada(self.db, "abc-123", "carro")
        self.assertEqual(r["placa"], "ABC123")

    def test_placa_moto_valida(self):
        crear_cliente(self.db, "2", "XYZ12A", "Moto")
        r = est.registrar_entrada(self.db, "XYZ12A", "Moto")
        self.assertEqual(r["tipo_vehiculo"], "Moto")
        self.assertTrue(int(r["celda_numero"].split("-")[1]) > 40)  # celdas de moto

    def test_placas_invalidas(self):
        for p in ["", "AB123", "ABCD123", "123ABC", "AB-1234", "!!!***", "ABC1234"]:
            rechazo(self, "PLACA_INVALIDA", est.registrar_entrada, self.db, p, "Carro")

    def test_tipo_invalido(self):
        rechazo(self, "TIPO_INVALIDO", est.registrar_entrada, self.db, "ABC123", "Bicicleta")
        rechazo(self, "TIPO_INVALIDO", est.registrar_entrada, self.db, "ABC123", "")

    def test_placa_incoherente_con_tipo(self):
        rechazo(self, "PLACA_TIPO_INCOHERENTE", est.registrar_entrada, self.db, "ABC12D", "Carro")
        rechazo(self, "PLACA_TIPO_INCOHERENTE", est.registrar_entrada, self.db, "ABC123", "Moto")


class TestMensualidad(Base):
    def test_sin_usuario_rechaza(self):
        rechazo(self, "SIN_MENSUALIDAD", est.registrar_entrada, self.db, "ABC123", "Carro")

    def test_sin_mensualidad_rechaza(self):
        crear_cliente(self.db, con_mensualidad=False)
        rechazo(self, "SIN_MENSUALIDAD", est.registrar_entrada, self.db, "ABC123", "Carro")

    def test_mensualidad_vencida_o_cancelada_rechaza(self):
        u = crear_cliente(self.db)
        m = self.db.query(models.Mensualidad).first()
        import datetime
        m.fecha_fin = datetime.date.today() - datetime.timedelta(days=1)
        self.db.commit()
        rechazo(self, "SIN_MENSUALIDAD", est.registrar_entrada, self.db, "ABC123", "Carro")
        # renovar y luego cancelar
        men.crear_mensualidad(self.db, u["id"], "ABC123")
        mid = self.db.query(models.Mensualidad).order_by(models.Mensualidad.id.desc()).first().id
        men.cancelar_mensualidad(self.db, mid)
        rechazo(self, "SIN_MENSUALIDAD", est.registrar_entrada, self.db, "ABC123", "Carro")

    def test_usuario_inactivo_rechaza(self):
        u = crear_cliente(self.db)
        usr.cambiar_estado_usuario(self.db, u["id"], "Inactivo")
        rechazo(self, "USUARIO_INACTIVO", est.registrar_entrada, self.db, "ABC123", "Carro")

    def test_tarifas_de_ejemplo_y_no_duplicar_vigente(self):
        u = crear_cliente(self.db)
        m = men.listar_mensualidades(self.db)[0]
        self.assertEqual(m["valor_mensual"], 180000)
        self.assertEqual(m["estado"], "Vigente")
        rechazo(self, "MENSUALIDAD_VIGENTE", men.crear_mensualidad, self.db, u["id"], "ABC123")

    def test_tipo_no_coincide_con_el_registrado(self):
        crear_cliente(self.db, "5", "ABC123", "Carro")
        rechazo(self, "PLACA_TIPO_INCOHERENTE", est.registrar_entrada, self.db, "ABC123", "Moto")


class TestDuplicadosYSalida(Base):
    def test_ingreso_duplicado_rechazado(self):
        crear_cliente(self.db)
        est.registrar_entrada(self.db, "ABC123", "Carro")
        rechazo(self, "PLACA_DUPLICADA", est.registrar_entrada, self.db, "ABC123", "Carro")
        self.assertEqual(len(est.listar_estancias(self.db, "activas")), 1)

    def test_salida_libera_solo_su_celda(self):
        crear_cliente(self.db, "1", "AAA111")
        crear_cliente(self.db, "2", "BBB222")
        a = est.registrar_entrada(self.db, "AAA111", "Carro")
        b = est.registrar_entrada(self.db, "BBB222", "Carro")
        self.assertNotEqual(a["celda_id"], b["celda_id"])
        est.registrar_salida(self.db, "AAA111")
        estados = {c["numero"]: c["estado"] for c in cel.listar_celdas(self.db)}
        self.assertEqual(estados[a["celda_numero"]], "Disponible")
        self.assertEqual(estados[b["celda_numero"]], "Ocupada")   # la otra NO se libera

    def test_salida_sin_estancia_y_doble_salida(self):
        crear_cliente(self.db)
        rechazo(self, "SIN_ESTANCIA_ACTIVA", est.registrar_salida, self.db, "ABC123")
        est.registrar_entrada(self.db, "ABC123", "Carro")
        r = est.registrar_salida(self.db, "abc-123")
        self.assertIn("mensualidad", r["mensaje"])
        self.assertNotIn("$", r["mensaje"])  # ya no hay cobro por hora
        rechazo(self, "SIN_ESTANCIA_ACTIVA", est.registrar_salida, self.db, "ABC123")

    def test_reingreso_despues_de_salir(self):
        crear_cliente(self.db)
        est.registrar_entrada(self.db, "ABC123", "Carro")
        est.registrar_salida(self.db, "ABC123")
        est.registrar_entrada(self.db, "ABC123", "Carro")
        self.assertEqual(len(est.listar_estancias(self.db, "todas")), 2)


class TestConsulta(Base):
    def test_finalizadas_con_horas(self):
        crear_cliente(self.db)
        est.registrar_entrada(self.db, "ABC123", "Carro")
        self.assertEqual(est.listar_estancias(self.db, "finalizadas"), [])  # sin resultados
        est.registrar_salida(self.db, "ABC123")
        fin = est.listar_estancias(self.db, "finalizadas")
        self.assertEqual(len(fin), 1)
        f = fin[0]
        self.assertEqual(f["placa"], "ABC123")
        self.assertIsNotNone(f["hora_entrada"]); self.assertIsNotNone(f["hora_salida"])
        self.assertIsNotNone(f["celda_numero"]); self.assertIn("min", f["duracion_texto"])
        self.assertEqual(est.listar_estancias(self.db, "activas"), [])
        self.assertEqual(len(est.listar_estancias(self.db, "finalizadas", placa="abc-123")), 1)
        self.assertEqual(est.listar_estancias(self.db, "finalizadas", placa="ZZZ999"), [])
        rechazo(self, "FILTRO_INVALIDO", est.listar_estancias, self.db, "otra")


class TestCeldas(Base):
    def test_50_celdas_y_tipos(self):
        r = cel.resumen_celdas(self.db)
        self.assertEqual(r["total"], 50)
        tipos = [c["tipo"] for c in cel.listar_celdas(self.db)]
        self.assertEqual((tipos.count("Carro"), tipos.count("Moto")), (40, 10))

    def test_no_se_puede_poner_en_mantenimiento_una_celda_ocupada(self):
        crear_cliente(self.db)
        r = est.registrar_entrada(self.db, "ABC123", "Carro")
        rechazo(self, "CELDA_OCUPADA", cel.cambiar_estado_celda, self.db, r["celda_id"], "Mantenimiento")
        rechazo(self, "ESTADO_INVALIDO", cel.cambiar_estado_celda, self.db, r["celda_id"], "Disponible" if False else "Ocupada")

    def test_mantenimiento_excluye_celda_de_la_asignacion(self):
        crear_cliente(self.db)
        primera = [c for c in cel.listar_celdas(self.db) if c["tipo"] == "Carro"][0]
        cel.cambiar_estado_celda(self.db, primera["id"], "Mantenimiento")
        r = est.registrar_entrada(self.db, "ABC123", "Carro")
        self.assertNotEqual(r["celda_id"], primera["id"])
        cel.cambiar_estado_celda(self.db, primera["id"], "Disponible")

    def test_sin_celdas_disponibles(self):
        for c in cel.listar_celdas(self.db):
            if c["tipo"] == "Moto":
                cel.cambiar_estado_celda(self.db, c["id"], "Mantenimiento")
        crear_cliente(self.db, "9", "XYZ12A", "Moto")
        rechazo(self, "CELDA_NO_DISPONIBLE", est.registrar_entrada, self.db, "XYZ12A", "Moto")

    def test_crear_celda(self):
        c = cel.crear_celda(self.db, "b-1", "moto")
        self.assertEqual((c["numero"], c["tipo"], c["estado"]), ("B-1", "Moto", "Disponible"))
        rechazo(self, "CELDA_DUPLICADA", cel.crear_celda, self.db, "B-1", "Moto")
        rechazo(self, "CELDA_INVALIDA", cel.crear_celda, self.db, "xx 1", "Moto")


class TestUsuarios(Base):
    def test_crud_y_duplicados(self):
        u = usr.crear_usuario(self.db, "CC", "12345678", "ana  maría ruiz", "3101234567", "ANA@X.CO")
        self.assertEqual(u["nombre"], "ana maría ruiz"); self.assertEqual(u["email"], "ana@x.co")
        rechazo(self, "USUARIO_DUPLICADO", usr.crear_usuario, self.db, "CC", "12345678", "Otra Persona")
        rechazo(self, "DOCUMENTO_INVALIDO", usr.crear_usuario, self.db, "XX", "12345678", "Otra Persona")
        rechazo(self, "DOCUMENTO_INVALIDO", usr.crear_usuario, self.db, "CC", "12", "Otra Persona")
        rechazo(self, "NOMBRE_INVALIDO", usr.crear_usuario, self.db, "CC", "99999", "A")
        rechazo(self, "TELEFONO_INVALIDO", usr.crear_usuario, self.db, "CC", "99999", "Otra", "abc")
        rechazo(self, "EMAIL_INVALIDO", usr.crear_usuario, self.db, "CC", "99999", "Otra", None, "no-es-mail")
        usr.actualizar_usuario(self.db, u["id"], telefono="3000000000")
        self.assertEqual(usr.obtener_usuario(self.db, u["id"])["telefono"], "3000000000")
        self.assertEqual(len(usr.listar_usuarios(self.db, "ana")), 1)
        rechazo(self, "USUARIO_NO_ENCONTRADO", usr.obtener_usuario, self.db, 999)

    def test_placa_unica_en_sistema(self):
        crear_cliente(self.db, "1", "ABC123")
        u2 = usr.crear_usuario(self.db, "CC", "22222", "Otra Persona")
        rechazo(self, "PLACA_REGISTRADA", usr.agregar_vehiculo, self.db, u2["id"], "ABC123", "Carro")


class TestConcurrencia(Base):
    def _hilos(self, tareas):
        self.db.rollback()  # la sesión de prueba no debe retener el bloqueo de escritura de SQLite
        resultados, lock = [], threading.Lock()
        barrera = threading.Barrier(len(tareas))

        def correr(fn):
            db = SessionLocal()
            try:
                barrera.wait()
                r = ("ok", fn(db))
            except ErrorNegocio as e:
                r = ("rechazo", e.codigo)
            except Exception as e:  # cualquier otra cosa es un fallo real
                r = ("error", repr(e))
            finally:
                db.close()
            with lock:
                resultados.append(r)

        hs = [threading.Thread(target=correr, args=(t,)) for t in tareas]
        [h.start() for h in hs]; [h.join() for h in hs]
        return resultados

    def test_misma_placa_simultanea_solo_una_estancia(self):
        crear_cliente(self.db)
        res = self._hilos([lambda db: est.registrar_entrada(db, "ABC123", "Carro")] * 8)
        self.assertEqual([r[0] for r in res].count("ok"), 1, res)
        self.assertFalse([r for r in res if r[0] == "error"], res)
        self.assertEqual(len(est.listar_estancias(self.db, "activas")), 1)

    def test_celdas_nunca_se_asignan_dos_veces(self):
        # Dejamos solo 3 celdas de moto libres y 8 motos intentando entrar a la vez.
        for c in cel.listar_celdas(self.db):
            if c["tipo"] == "Moto" and c["id"] not in [x["id"] for x in cel.listar_celdas(self.db) if x["tipo"] == "Moto"][:3]:
                cel.cambiar_estado_celda(self.db, c["id"], "Mantenimiento")
        placas = [f"MOT{i:02d}A" for i in range(8)]
        for i, p in enumerate(placas):
            crear_cliente(self.db, f"70{i}", p, "Moto")
        res = self._hilos([(lambda p: (lambda db: est.registrar_entrada(db, p, "Moto")))(p) for p in placas])
        oks = [r for r in res if r[0] == "ok"]
        self.assertEqual(len(oks), 3, res)
        self.assertFalse([r for r in res if r[0] == "error"], res)
        self.assertEqual(len({r[1]["celda_id"] for r in oks}), 3)  # 3 celdas distintas
        self.assertTrue(all(r[1] == "CELDA_NO_DISPONIBLE" for r in res if r[0] == "rechazo"), res)


class TestMigracion(unittest.TestCase):
    def test_bd_de_iteracion_1_se_migra_y_repara(self):
        with engine.begin() as con:
            for t in ["registros", "celdas", "mensualidades", "vehiculos", "usuarios"]:
                con.execute(text(f"DROP TABLE IF EXISTS {t}"))
            con.execute(text("CREATE TABLE celdas (id INTEGER PRIMARY KEY, numero VARCHAR UNIQUE, estado VARCHAR)"))
            con.execute(text("CREATE TABLE registros (id INTEGER PRIMARY KEY, placa VARCHAR, tipo_vehiculo VARCHAR,"
                             " hora_entrada DATETIME, hora_salida DATETIME, celda_id INTEGER)"))
            for i in range(1, 51):
                con.execute(text("INSERT INTO celdas(numero, estado) VALUES (:n, 'Disponible')"), {"n": f"A-{i}"})
            # Estado dejado por el viejo /reset-celdas: vehículo dentro, celda 'Disponible'
            con.execute(text("INSERT INTO registros(placa,tipo_vehiculo,hora_entrada,celda_id) VALUES ('abc-123','Carro','2026-10-01 10:00:00',1)"))
            # Celda 'Ocupada' sin vehículo
            con.execute(text("UPDATE celdas SET estado='Ocupada' WHERE numero='A-5'"))
        models.Base.metadata.create_all(bind=engine)   # crea solo tablas nuevas
        migrar(engine); migrar(engine)                 # idempotente
        sincronizar_celdas(engine)
        db = SessionLocal()
        try:
            c = {x["numero"]: x for x in cel.listar_celdas(db)}
            self.assertEqual(c["A-1"]["estado"], "Ocupada")
            self.assertEqual(c["A-1"]["placa"], "ABC123")      # placa normalizada
            self.assertEqual(c["A-5"]["estado"], "Disponible")
            self.assertEqual((c["A-40"]["tipo"], c["A-41"]["tipo"]), ("Carro", "Moto"))
            db.rollback()
            # el índice único quedó activo
            with self.assertRaises(Exception):
                with engine.begin() as con:
                    con.execute(text("INSERT INTO registros(placa,tipo_vehiculo,hora_entrada,celda_id) VALUES ('ABC123','Carro','2026-10-02',2)"))
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
