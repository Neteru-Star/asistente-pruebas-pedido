"""HU-10: decide qué archivos se pueden enviar a la API de IA."""


class ArchivoProhibidoError(Exception):
    """La selección incluye un archivo que nunca puede salir del equipo."""


def filtrar_envio(seleccion: list[str], permitidas: list[str]) -> list[str]:
    """Devuelve las rutas de la selección que están en la lista permitida.

    Lanza ArchivoProhibidoError si la selección incluye un .env o una base de datos.
    """
    rutas = []
    for ruta in seleccion:
        r = ruta.replace("\\", "/")
        if r.startswith("./"):
            r = r[2:]
        nombre = r.split("/")[-1].lower()
        if nombre == ".env" or nombre.startswith(".env.") or nombre.endswith((".db", ".sqlite", ".sqlite3")):
            raise ArchivoProhibidoError(f"El archivo {ruta} no se puede enviar")
        rutas.append(r)

    permitidas_normalizadas = []
    for p in permitidas:
        p = p.replace("\\", "/")
        if p.startswith("./"):
            p = p[2:]
        permitidas_normalizadas.append(p)

    resultado = []
    for r in rutas:
        if r in permitidas_normalizadas and r not in resultado:
            resultado.append(r)
    return resultado
