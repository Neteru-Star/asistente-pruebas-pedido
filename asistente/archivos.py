"""HU-10: decide qué archivos se pueden enviar a la API de IA."""

NOMBRE_ENV = ".env"
EXTENSIONES_BASE_DE_DATOS = (".db", ".sqlite", ".sqlite3")


class ArchivoProhibidoError(Exception):
    """La selección incluye un archivo que nunca puede salir del equipo."""


def _normalizar(ruta: str) -> str:
    """Escribe la ruta con "/" y sin el "./" inicial."""
    ruta = ruta.replace("\\", "/")
    if ruta.startswith("./"):
        ruta = ruta[2:]
    return ruta


def _es_prohibido(ruta: str) -> bool:
    """Indica si la ruta es un .env, una variante .env.* o una base de datos."""
    nombre = ruta.split("/")[-1].lower()
    es_env = nombre == NOMBRE_ENV or nombre.startswith(NOMBRE_ENV + ".")
    return es_env or nombre.endswith(EXTENSIONES_BASE_DE_DATOS)


def filtrar_envio(seleccion: list[str], permitidas: list[str]) -> list[str]:
    """Devuelve las rutas de la selección que están en la lista permitida.

    Lanza ArchivoProhibidoError si la selección incluye un .env o una base de datos.
    """
    for ruta in seleccion:
        if _es_prohibido(_normalizar(ruta)):
            raise ArchivoProhibidoError(f"El archivo {ruta} no se puede enviar")

    permitidas_normalizadas = {_normalizar(p) for p in permitidas}
    resultado = []
    for ruta in seleccion:
        normalizada = _normalizar(ruta)
        if normalizada in permitidas_normalizadas and normalizada not in resultado:
            resultado.append(normalizada)
    return resultado
