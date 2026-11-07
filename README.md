# Asistente de pruebas del módulo de pedidos

Proyecto final del Seminario de IA aplicada al ciclo de vida del software. Es una herramienta de línea de
comandos en Python que usa IA para proponer pruebas pytest del módulo de pedidos de una aplicación de
inventario para una papelería. Las decisiones sobre cada prueba las toma una persona del equipo.

Estudiante: David Felipe Deulufeutt Cortinez

## Funcionalidad de la semana 5

### Historia de usuario

**HU-10 (Must).** Como desarrollador, quiero que al asistente solo se le envíe el código del módulo de
pedidos e inventario y datos de prueba inventados, para que las claves y los datos de los clientes de la
papelería no salgan del equipo. Necesidad de origen: N-12. Requisito no funcional relacionado: RNF-04.

Criterios de aceptación:

- **Escenario 1: envío permitido.** Dado que selecciono el código del módulo de pedidos y el archivo de datos
  de prueba con clientes tipo «Cliente Prueba 1», cuando pido pruebas al asistente, entonces solo se envían
  esos archivos.
- **Escenario 2 (error): archivo prohibido.** Dado que la selección incluye el archivo .env, cuando pido
  pruebas al asistente, entonces no se envía nada y se indica que el archivo .env no se puede enviar.

### Contrato

```python
def filtrar_envio(seleccion: list[str], permitidas: list[str]) -> list[str]
```

Está en `asistente/archivos.py`.

- **Recibe:** `seleccion`, las rutas que el desarrollador quiere enviar a la API de IA, y `permitidas`, la
  lista permitida del repositorio. Las dos son rutas relativas a la raíz del repositorio.
- **Devuelve:** las rutas de `seleccion` que están en `permitidas`, en el mismo orden, sin repetidas y
  escritas con `/`.
- **Error:** si la selección incluye un archivo prohibido, lanza `ArchivoProhibidoError` con el mensaje
  `El archivo <ruta> no se puede enviar` y no devuelve nada. Son prohibidos:
  - `.env` y cualquier variante `.env.*` (por ejemplo `.env.local` o `.env.example`), en cualquier carpeta y
    con cualquier combinación de mayúsculas;
  - las bases de datos (`.db`, `.sqlite`, `.sqlite3`), aunque estén en la lista permitida.

Supuestos:

- Un archivo que no está en la lista y no es prohibido se omite sin error, como pide el escenario 1.
- La lista permitida usa rutas exactas, no patrones como `app/*.py`, para que se sepa con precisión qué sale
  hacia la API.
- `app\pedidos.py` y `./app/pedidos.py` se tratan como `app/pedidos.py`.
- Un nombre parecido no basta: `app/pedidos.py.bak` no coincide con `app/pedidos.py`.

Casos límite: selección vacía, rutas con `\` o `./`, archivos repetidos, nombres parecidos a uno permitido,
`.env` en una subcarpeta o en mayúsculas, y una base de datos incluida por error en la lista permitida.

Ejemplos, con `permitidas = ["app/pedidos.py", "app/inventario.py", "datos/semilla.sql"]`:

| Selección | Resultado |
|---|---|
| `["app/pedidos.py", "datos/semilla.sql", "app/reportes.py"]` | `["app/pedidos.py", "datos/semilla.sql"]` |
| `[]` | `[]` |
| `["app\\pedidos.py", "./app/pedidos.py"]` | `["app/pedidos.py"]` |
| `["app/pedidos.py", ".env"]` | `ArchivoProhibidoError: El archivo .env no se puede enviar` |

### Cómo ejecutar las pruebas

Requiere Python 3.10 o superior. Funciona igual en Windows, macOS y Linux.

```bash
python -m venv .venv
```

Activa el entorno (`.venv\Scripts\activate` en Windows, `source .venv/bin/activate` en macOS y Linux) y luego:

```bash
pip install -r requirements.txt
```

```bash
pytest
```

Las pruebas están en `tests/test_archivos.py`.

## Seguridad

El archivo `.env` y las bases de datos están en `.gitignore`. El repositorio no contiene claves ni datos
reales.
