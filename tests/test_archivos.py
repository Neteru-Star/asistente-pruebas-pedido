import pytest

from asistente.archivos import ArchivoProhibidoError, filtrar_envio

PERMITIDAS = ["app/pedidos.py", "app/inventario.py", "datos/semilla.sql"]


# Casos normales

def test_envia_solo_los_archivos_de_la_lista_permitida():
    seleccion = ["app/pedidos.py", "datos/semilla.sql", "app/reportes.py"]
    assert filtrar_envio(seleccion, PERMITIDAS) == ["app/pedidos.py", "datos/semilla.sql"]


def test_conserva_el_orden_de_la_seleccion():
    seleccion = ["datos/semilla.sql", "app/inventario.py", "app/pedidos.py"]
    assert filtrar_envio(seleccion, PERMITIDAS) == seleccion


# Casos límite

def test_seleccion_vacia_no_envia_nada():
    assert filtrar_envio([], PERMITIDAS) == []


def test_rutas_de_windows_y_con_punto_se_normalizan():
    seleccion = [r"app\pedidos.py", "./datos/semilla.sql"]
    assert filtrar_envio(seleccion, PERMITIDAS) == ["app/pedidos.py", "datos/semilla.sql"]


def test_archivo_repetido_se_envia_una_sola_vez():
    seleccion = ["app/pedidos.py", "./app/pedidos.py", r"app\pedidos.py"]
    assert filtrar_envio(seleccion, PERMITIDAS) == ["app/pedidos.py"]


def test_nombre_parecido_a_uno_permitido_no_se_envia():
    seleccion = ["app/pedidos.py.bak", "app/pedidos_viejo.py"]
    assert filtrar_envio(seleccion, PERMITIDAS) == []


# Casos de error (HU-10, escenario 2)

def test_seleccion_con_env_no_envia_nada_e_indica_el_archivo():
    with pytest.raises(ArchivoProhibidoError, match=r"El archivo \.env no se puede enviar"):
        filtrar_envio(["app/pedidos.py", ".env"], PERMITIDAS)


@pytest.mark.parametrize("ruta", ["config/.env", ".ENV", ".env.local", ".env.example"])
def test_variantes_de_env_tambien_se_bloquean(ruta):
    with pytest.raises(ArchivoProhibidoError, match="no se puede enviar"):
        filtrar_envio([ruta], PERMITIDAS)


def test_base_de_datos_real_se_bloquea_aunque_este_en_la_lista():
    permitidas = PERMITIDAS + ["instance/papeleria.db"]
    with pytest.raises(ArchivoProhibidoError, match="papeleria.db"):
        filtrar_envio(["instance/papeleria.db"], permitidas)


# Pruebas de abuso agregadas en la revisión de la semana 6

@pytest.mark.parametrize(
    "ruta",
    [
        "instance/papeleria.db-wal",
        "instance/papeleria.db-journal",
        "instance/papeleria.db-shm",
        "backup/papeleria.db.bak",
        "datos/clientes.sqlite3-wal",
    ],
)
def test_archivos_auxiliares_y_copias_de_la_base_de_datos_se_bloquean(ruta):
    with pytest.raises(ArchivoProhibidoError, match="no se puede enviar"):
        filtrar_envio([ruta], [ruta])


@pytest.mark.parametrize("ruta", ["prod.env", ".envrc", "certs/servidor.pem", "claves/api.key"])
def test_otros_archivos_de_secretos_se_bloquean(ruta):
    with pytest.raises(ArchivoProhibidoError, match="no se puede enviar"):
        filtrar_envio([ruta], [ruta])


def test_nombre_con_db_en_medio_que_no_es_base_de_datos_se_envia():
    assert filtrar_envio(["app/dbutils.py"], ["app/dbutils.py"]) == ["app/dbutils.py"]


@pytest.mark.parametrize(
    "ruta",
    [".env::$DATA", "instance/papeleria.db::$DATA", ".env ", ".env.", "instance/papeleria.db."],
)
def test_rutas_equivalentes_en_windows_se_bloquean(ruta):
    with pytest.raises(ArchivoProhibidoError, match="no se puede enviar"):
        filtrar_envio([ruta], [ruta])


def test_nombre_corto_de_windows_se_bloquea():
    # En NTFS, ENV~1 es el nombre corto 8.3 de .env y abre el mismo archivo
    with pytest.raises(ArchivoProhibidoError, match="ENV~1"):
        filtrar_envio(["ENV~1"], ["ENV~1"])


@pytest.mark.parametrize("ruta", ["././app/pedidos.py", "app//pedidos.py", "app/./pedidos.py"])
def test_rutas_con_partes_redundantes_se_normalizan(ruta):
    assert filtrar_envio([ruta], PERMITIDAS) == ["app/pedidos.py"]


@pytest.mark.parametrize(
    "ruta", ["../app/pedidos.py", "/app/pedidos.py", "otro/../../app/pedidos.py"]
)
def test_rutas_fuera_del_repositorio_no_se_envian(ruta):
    assert filtrar_envio([ruta], PERMITIDAS) == []


@pytest.mark.parametrize(
    ("seleccion", "permitidas"),
    [("app/pedidos.py", PERMITIDAS), ([None], PERMITIDAS), (["app/pedidos.py"], "app/pedidos.py")],
)
def test_entradas_que_no_son_listas_de_rutas_lanzan_type_error(seleccion, permitidas):
    with pytest.raises(TypeError, match="lista de rutas"):
        filtrar_envio(seleccion, permitidas)


def test_mensaje_de_error_no_incluye_caracteres_de_control():
    with pytest.raises(ArchivoProhibidoError) as error:
        filtrar_envio(["x\x1b[2J/.env"], PERMITIDAS)
    assert str(error.value) == "El archivo x?[2J/.env no se puede enviar"
