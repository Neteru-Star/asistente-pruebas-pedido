# Asistente de pruebas del módulo de pedidos

## 1. Qué es

Proyecto final del Seminario de IA aplicada al ciclo de vida del software. Es una herramienta de línea de
comandos en Python que usa IA para proponer pruebas pytest del módulo de pedidos de una aplicación de
inventario para una papelería. Las decisiones sobre cada prueba las toma una persona del equipo.

Este primer incremento implementa la historia HU-10: antes de enviar código a la API de IA, la función
`filtrar_envio` decide qué archivos pueden salir del equipo. Nunca deja pasar el `.env` ni la base de datos
real, que tiene unos 200 clientes (RNF-04).

## 2. Requisitos

- Python 3.10 o superior, en Windows, macOS o Linux.
- Git, para clonar el repositorio.
- No necesita internet ni claves para ejecutar las pruebas. La clave de la API de IA se usará en un incremento
  posterior; su plantilla está en `.env.example`.

## 3. Instalación

```bash
git clone https://github.com/Neteru-Star/asistente-pruebas-pedido.git
```

```bash
cd asistente-pruebas-pedido
```

```bash
python -m venv .venv
```

Activa el entorno: en Windows `.venv\Scripts\activate`, y en macOS o Linux `source .venv/bin/activate`. Luego:

```bash
pip install -r requirements-dev.txt
```

`requirements.txt` tiene lo necesario para las pruebas (pytest) y `requirements-dev.txt` agrega el linter y la
auditoría de dependencias (ruff y pip-audit). Todas las versiones están fijadas.

## 4. Ejecución

La herramienta todavía no tiene comando propio; por ahora la funcionalidad se usa como función de Python:

```bash
python -c "from asistente.archivos import filtrar_envio; print(filtrar_envio(['app/pedidos.py', 'app/reportes.py'], ['app/pedidos.py']))"
```

Resultado: `['app/pedidos.py']`. Si la selección incluye un archivo prohibido, la función lanza
`ArchivoProhibidoError`:

```bash
python -c "from asistente.archivos import filtrar_envio; filtrar_envio(['.env'], [])"
```

Resultado: `asistente.archivos.ArchivoProhibidoError: El archivo .env no se puede enviar`.

## 5. Pruebas

```bash
pytest
```

Las 44 pruebas están en `tests/test_archivos.py`. Para revisar el estilo y la seguridad del código:

```bash
ruff check .
```

```bash
pip-audit -r requirements-dev.txt
```

La revisión de seguridad de la semana 6 está en [revision_seguridad.md](revision_seguridad.md).

## 6. Estructura

```
asistente-pruebas-pedido/
├── asistente/
│   ├── __init__.py
│   └── archivos.py           HU-10: filtrar_envio y ArchivoProhibidoError
├── tests/
│   └── test_archivos.py      pruebas normales, de límite, de error y de abuso
├── .env.example              plantilla de variables de entorno, sin valores reales
├── .gitignore                ignora .env, bases de datos y el entorno virtual
├── bitacora_ia.md            decisiones sobre las sugerencias de la IA
├── pyproject.toml            configuración de ruff
├── pytest.ini                configuración de pytest
├── requirements.txt          dependencias para las pruebas
├── requirements-dev.txt      dependencias de desarrollo: ruff y pip-audit
└── revision_seguridad.md     informe de revisión de código y seguridad
```

## 7. Uso de IA

El código se escribió con Claude Code (modelo Claude Opus 5.5) como asistente. Las pruebas se escribieron
antes que la implementación, y cada sugerencia se aceptó, se ajustó o se rechazó según el contrato, las pruebas
y RNF-04. La segunda revisión de la semana 6 la hizo un agente revisor independiente, y cada hallazgo se
verificó en el código antes de corregirlo. Todo está registrado en [bitacora_ia.md](bitacora_ia.md) y en
[revision_seguridad.md](revision_seguridad.md).

## 8. Autor y licencia

David Felipe Deulufeutt Cortinez. Trabajo académico para la Fundación Escuela Tecnológica de Neiva Jesús Oviedo
Pérez. Sin licencia de código abierto: todos los derechos reservados al autor.

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
  lista permitida del repositorio. Las dos son listas de rutas relativas a la raíz del repositorio.
- **Devuelve:** las rutas de `seleccion` que están en `permitidas`, en el mismo orden, sin repetidas y
  normalizadas: con `/` y sin `./` ni `//`.
- **Errores:**
  - `TypeError` si `seleccion` o `permitidas` no son una lista o tupla de textos.
  - `ArchivoProhibidoError` con el mensaje `El archivo <ruta> no se puede enviar` si la selección incluye un
    archivo prohibido, aunque esté en la lista permitida. En ese caso no devuelve nada. Son prohibidos:
    - `.env` y sus variantes (`.env.local`, `.env.example`, `prod.env`, `.envrc`), en cualquier carpeta y
      con cualquier combinación de mayúsculas;
    - las bases de datos `.db`, `.sqlite` y `.sqlite3`, sus archivos auxiliares (`-wal`, `-journal`, `-shm`)
      y sus copias (`.db.bak`);
    - las claves privadas `.pem` y `.key`;
    - las rutas que en Windows pueden abrir otro archivo: con `:` (como `.env::$DATA`), con un nombre corto
      8.3 (como `ENV~1`) o con puntos o espacios finales (como `.env `).

Supuestos:

- Un archivo que no está en la lista y no es prohibido se omite sin error, como pide el escenario 1.
- La lista permitida usa rutas exactas, no patrones como `app/*.py`, para que se sepa con precisión qué sale
  hacia la API.
- `app\pedidos.py`, `./app/pedidos.py` y `app//pedidos.py` se tratan como `app/pedidos.py`.
- Las rutas que salen del repositorio, como `../app/pedidos.py` o `/app/pedidos.py`, no coinciden con la lista
  y se omiten.
- Un nombre parecido no basta: `app/pedidos.py.bak` no coincide con `app/pedidos.py`.
- En el mensaje de error, los caracteres de control de la ruta se muestran como `?`.

Casos límite: selección vacía, rutas con `\`, `./` o `//`, archivos repetidos, nombres parecidos a uno
permitido, `.env` en una subcarpeta o en mayúsculas, y una base de datos incluida por error en la lista
permitida.

Ejemplos, con `permitidas = ["app/pedidos.py", "app/inventario.py", "datos/semilla.sql"]`:

| Selección | Resultado |
|---|---|
| `["app/pedidos.py", "datos/semilla.sql", "app/reportes.py"]` | `["app/pedidos.py", "datos/semilla.sql"]` |
| `[]` | `[]` |
| `["app\\pedidos.py", "./app/pedidos.py"]` | `["app/pedidos.py"]` |
| `["app/pedidos.py", ".env"]` | `ArchivoProhibidoError: El archivo .env no se puede enviar` |
| `["instance/papeleria.db-wal"]` | `ArchivoProhibidoError: El archivo instance/papeleria.db-wal no se puede enviar` |

### Cómo ejecutar las pruebas

Con el entorno activado, desde la raíz del repositorio:

```bash
pytest
```
