"""HU-10: decide qué archivos se pueden enviar a la API de IA."""

import re

NOMBRE_ENV = ".env"
NOMBRES_ENV_EXTRA = (".envrc",)
# .db, .sqlite o .sqlite3 al final o seguidos de "-" o "." (papeleria.db-wal, papeleria.db.bak)
PATRON_BASE_DE_DATOS = re.compile(r"\.(db|sqlite3?)([.-]|$)")
EXTENSIONES_CLAVES = (".pem", ".key")


class ArchivoProhibidoError(Exception):
    """La selección incluye un archivo que nunca puede salir del equipo."""


def _normalizar(ruta: str) -> str:
    """Escribe la ruta con "/" y sin el "./" inicial."""
    ruta = ruta.replace("\\", "/")
    if ruta.startswith("./"):
        ruta = ruta[2:]
    return ruta


def _es_prohibido(ruta: str) -> bool:
    """Indica si la ruta es un .env o una variante, una base de datos o una clave privada."""
    nombre = ruta.split("/")[-1].lower()
    es_env = (
        nombre == NOMBRE_ENV
        or nombre.startswith(NOMBRE_ENV + ".")
        or nombre.endswith(NOMBRE_ENV)
        or nombre in NOMBRES_ENV_EXTRA
    )
    es_base_de_datos = PATRON_BASE_DE_DATOS.search(nombre) is not None
    return es_env or es_base_de_datos or nombre.endswith(EXTENSIONES_CLAVES)


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
