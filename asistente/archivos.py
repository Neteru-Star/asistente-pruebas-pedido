"""HU-10: decide qué archivos se pueden enviar a la API de IA.

Protege RNF-04: ningún contenido del .env ni de la base de datos real llega a la IA.
"""

import posixpath
import re

NOMBRE_ENV = ".env"
NOMBRES_ENV_EXTRA = (".envrc",)
# .db, .sqlite o .sqlite3 al final o seguidos de "-" o "." (papeleria.db-wal, papeleria.db.bak)
PATRON_BASE_DE_DATOS = re.compile(r"\.(db|sqlite3?)([.-]|$)")
EXTENSIONES_CLAVES = (".pem", ".key")
# Nombre corto 8.3 de Windows, como ENV~1: puede abrir cualquier archivo, incluido el .env
PATRON_NOMBRE_CORTO = re.compile(r"~\d")


class ArchivoProhibidoError(Exception):
    """La selección incluye un archivo que nunca puede salir del equipo."""


def _normalizar(ruta: str) -> str:
    """Escribe la ruta con "/" y sin partes redundantes como "./" o "//"."""
    return posixpath.normpath(ruta.replace("\\", "/"))


def _es_ambigua_en_windows(ruta: str, nombre: str) -> bool:
    """Indica si en Windows la ruta podría abrir otro archivo distinto del que parece.

    Cubre los flujos alternativos de NTFS (.env::$DATA), las rutas con unidad (C:/...) y los
    nombres cortos 8.3 (ENV~1).
    """
    return ":" in ruta or PATRON_NOMBRE_CORTO.search(nombre) is not None


def _es_env(nombre: str) -> bool:
    """Indica si el nombre es un .env o una variante (.env.local, prod.env, .envrc)."""
    return (
        nombre == NOMBRE_ENV
        or nombre.startswith(NOMBRE_ENV + ".")
        or nombre.endswith(NOMBRE_ENV)
        or nombre in NOMBRES_ENV_EXTRA
    )


def _es_prohibido(ruta: str) -> bool:
    """Indica si una ruta normalizada nunca se puede enviar a la IA.

    Args:
        ruta: ruta ya normalizada con _normalizar.

    Returns:
        True si es un .env o una variante, una base de datos o uno de sus archivos auxiliares,
        una clave privada, o una ruta ambigua en Windows.
    """
    # Windows ignora los puntos y espacios finales: ".env " abre el mismo archivo que ".env"
    nombre = ruta.split("/")[-1].lower().rstrip(". ")
    return (
        _es_ambigua_en_windows(ruta, nombre)
        or _es_env(nombre)
        or PATRON_BASE_DE_DATOS.search(nombre) is not None
        or nombre.endswith(EXTENSIONES_CLAVES)
    )


def _para_mostrar(ruta: str) -> str:
    """Reemplaza por "?" los caracteres de control, para que no alteren la terminal ni el log."""
    return "".join(caracter if caracter.isprintable() else "?" for caracter in ruta)


def _validar_rutas(rutas: object, parametro: str) -> None:
    """Lanza TypeError si rutas no es una lista o tupla de textos."""
    es_lista_de_textos = isinstance(rutas, (list, tuple)) and all(
        isinstance(ruta, str) for ruta in rutas
    )
    if not es_lista_de_textos:
        raise TypeError(f"{parametro} debe ser una lista de rutas de texto")


def filtrar_envio(seleccion: list[str], permitidas: list[str]) -> list[str]:
    """Devuelve las rutas de la selección que se pueden enviar a la API de IA.

    Primero revisa toda la selección: si hay un archivo prohibido, no devuelve nada. Después
    conserva solo las rutas que están en la lista permitida. Las rutas se comparan normalizadas,
    con "/" y sin "./" ni "//".

    Args:
        seleccion: rutas que el desarrollador quiere enviar, relativas a la raíz del repositorio.
        permitidas: rutas exactas de la lista permitida, sin patrones como app/*.py.

    Returns:
        Las rutas normalizadas de la selección que están en la lista permitida, en el mismo
        orden y sin repetidas. Las que no están en la lista se omiten sin error.

    Raises:
        TypeError: si seleccion o permitidas no son una lista o tupla de textos.
        ArchivoProhibidoError: si la selección incluye un .env o una variante, una base de
            datos o uno de sus archivos auxiliares, una clave privada o una ruta ambigua en
            Windows, aunque esté en la lista permitida. El mensaje es
            «El archivo <ruta> no se puede enviar».
    """
    _validar_rutas(seleccion, "seleccion")
    _validar_rutas(permitidas, "permitidas")
    normalizadas = [_normalizar(ruta) for ruta in seleccion]
    for original, normalizada in zip(seleccion, normalizadas, strict=True):
        if _es_prohibido(normalizada):
            raise ArchivoProhibidoError(
                f"El archivo {_para_mostrar(original)} no se puede enviar"
            )

    permitidas_normalizadas = {_normalizar(ruta) for ruta in permitidas}
    resultado = []
    vistas = set()
    for ruta in normalizadas:
        if ruta in permitidas_normalizadas and ruta not in vistas:
            vistas.add(ruta)
            resultado.append(ruta)
    return resultado
