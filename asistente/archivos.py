"""HU-10: decide qué archivos se pueden enviar a la API de IA."""


class ArchivoProhibidoError(Exception):
    """La selección incluye un archivo que nunca puede salir del equipo."""


def filtrar_envio(seleccion: list[str], permitidas: list[str]) -> list[str]:
    raise NotImplementedError("Pendiente: se implementa después de las pruebas")
