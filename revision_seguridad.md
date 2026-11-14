# Informe de revisión de código y seguridad

Proyecto: Pruebas asistidas por IA para el módulo de pedidos
Estudiante: David Felipe Deulufeutt Cortinez
Fecha: 2026-11-14
Commit revisado: c3066d7 (entrega de la semana 5)

## 1. Herramientas y criterios

- **Linter:** ruff 0.17.5 con las reglas E, F, B y S. Configuración en `pyproject.toml`.
- **Auditoría de dependencias:** pip-audit 2.10.1 sobre `requirements-dev.txt`. Resultado: sin vulnerabilidades
  conocidas.
- **Lista de revisión:** la de la semana 6, que cubre corrección y pruebas, diseño y legibilidad, y seguridad.
- **Revisión con IA:** un agente revisor independiente de Claude Code (Claude Opus 5.5), que solo podía leer,
  con el prompt de revisión de la semana (sección 3).

### Puntos de seguridad revisados

| Punto | ¿Aplica? | Resultado |
|---|---|---|
| Inyección (consultas con parámetros) | No hay SQL ni comandos del sistema: la función solo compara textos. Sí aplica a la salida en terminal. | Ver H-09 |
| Secretos (código, historial, .gitignore, .env.example) | Sí | `git log --all -p` no muestra claves y nunca se subió un `.env` ni una base de datos. Ver H-04 (`.env.example` estaba ignorado) |
| Contraseñas (scrypt, bcrypt o argon2 con sal) | No: la herramienta no tiene usuarios ni guarda contraseñas | No aplica |
| Control de acceso (rol verificado y prueba de abuso) | Sí: no hay roles, pero `filtrar_envio` es el control que decide qué sale hacia la IA (RNF-04) | Ver H-01, H-02, H-03 y H-06; de los 32 casos de prueba nuevos, 20 son de abuso (intentos de enviar un archivo prohibido) |
| Dependencias (existen, necesarias, versión fijada, pip-audit) | Sí | pytest, ruff y pip-audit existen, son necesarias y tienen versión fijada; pip-audit no encontró vulnerabilidades |

## 2. Tabla de hallazgos

Las líneas son las del commit revisado, c3066d7.

| Id | Archivo y línea | Problema | Categoría (OWASP o tipo) | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | asistente/archivos.py:4 y 23 | Solo bloqueaba `.db`, `.sqlite` y `.sqlite3`; pasaban `papeleria.db-wal`, `-journal`, `-shm` y `.db.bak`, que tienen datos reales | A01 Control de acceso roto | Media | Expresión regular `\.(db\|sqlite3?)([.-]\|$)` y pruebas de abuso | ac46672 |
| H-02 | asistente/archivos.py:21-23 | En Windows, `.env::$DATA`, `.env ` y `papeleria.db.` abren el archivo real, pero el filtro solo comparaba el texto | A01 Control de acceso roto (CWE-41) | Media | Rechazar rutas con `:` y quitar puntos y espacios finales; pruebas de abuso | cc0d40c |
| H-03 | asistente/archivos.py:21-23 | El nombre corto 8.3 `ENV~1` abre el `.env` en NTFS y pasaba el filtro | A01 Control de acceso roto (CWE-41) | Media | Rechazar nombres con `~` seguido de un dígito; prueba de abuso | cc0d40c |
| H-04 | .gitignore:3 y 6-8 | `.env.*` ignoraba `.env.example`, y `*.db` no cubría los archivos `-wal`, `-journal` ni las copias `.bak` | A05 Configuración insegura | Media | `!.env.example`, plantilla `.env.example` y patrones para archivos auxiliares e `instance/` | 88344e4 |
| H-05 | tests/test_archivos.py:48-57 | Dos versiones alteradas de la función pasaban las 12 pruebas: una que solo bloqueaba `.db` y otra que no normalizaba la lista permitida | Pruebas insuficientes | Media | Pruebas de `.sqlite`, `.sqlite3`, `.DB`, `\`, mensaje exacto y lista permitida con `\`; ahora esas versiones fallan | 364061d |
| H-06 | asistente/archivos.py:3 y 22 | No se bloqueaban `prod.env`, `.envrc`, `.pem` ni `.key` | A05 Configuración insegura (CWE-538) | Baja | Se agregan a los prohibidos, con pruebas de abuso | ac46672 |
| H-07 | asistente/archivos.py:11-16 | Solo quitaba un `./` inicial: `././app/pedidos.py` y `app//pedidos.py` se omitían aunque estuvieran permitidos | Corrección | Baja | `posixpath.normpath` y pruebas; las rutas con `..` o `/` siguen sin enviarse | 58f8b5f |
| H-08 | asistente/archivos.py:26-40 | Con un texto en lugar de una lista recorría sus letras, y con `None` fallaba con `AttributeError` | Validación de entrada (CWE-20) | Baja | `TypeError` con mensaje claro y pruebas | 60d6d8a |
| H-09 | asistente/archivos.py:33 | El mensaje de error copiaba la ruta con caracteres de control: `x\x1b[2J/.env` borra la pantalla al imprimirse | A03 Inyección (CWE-150) | Baja | Los caracteres no imprimibles se muestran como `?`; prueba nueva | bd7d16f |
| H-10 | asistente/archivos.py:27-39 | Cada ruta se normalizaba dos veces, la búsqueda de repetidas era sobre una lista y la docstring no describía el contrato | Diseño y legibilidad | Baja | Normalizar una vez, conjunto de vistas, funciones más cortas y docstrings completos | 745b5d9 |

**Severidad:** alta (permite acceder o cambiar datos sin permiso, o expone secretos), media (error probable o
riesgo con condiciones), baja (estilo o mantenibilidad). H-01 a H-03 son de severidad media y no alta porque solo
exponen datos si el archivo también está en la lista permitida; si no lo está, el filtro ya lo omitía.

### Avisos del linter no corregidos

Configuración en commit 449824d.

| Regla | Archivo y línea | Por qué se mantiene |
|---|---|---|
| S101 | tests/test_archivos.py (todas las pruebas) | `assert` es la forma normal de comprobar en pytest; se permite solo en `tests/` |
| E501 | tests/test_archivos.py:12, 28 y 44 | Se subió el límite a 100 caracteres en lugar de partir líneas de pruebas existentes, que no deben modificarse |

## 3. Revisión con IA

**Prompt usado:** se pidió al agente revisor que actuara como revisor de código y seguridad, sin modificar
archivos, con tres criterios (corrección y pruebas, diseño y legibilidad, seguridad), una tabla con línea,
categoría, severidad y corrección, y la tabla separada en «problemas seguros», con una entrada que lo demuestre,
y «sospechas». El texto completo está en la entrada 7 de [bitacora_ia.md](bitacora_ia.md).

| Hallazgo de la IA | ¿Real o falso positivo? | Cómo lo verifiqué |
|---|---|---|
| IA-01 Archivos auxiliares de SQLite | Real (H-01), pero la IA lo calificó como alta y es media | `filtrar_envio(["instance/papeleria.db-wal"], ...)` devolvía la ruta |
| IA-02 Rutas equivalentes en Windows | Real (H-02) | `.env::$DATA`, `.env ` y `papeleria.db.` pasaban el filtro |
| IA-03 .gitignore | Real (H-04) | `git check-ignore -v .env.example` respondía `.gitignore:3:.env.*` |
| IA-04 Pruebas insuficientes | Real (H-05) | Ejecuté las dos versiones alteradas: antes pasaban; ahora fallan 7 y 1 pruebas |
| IA-05 Caracteres de control en el mensaje | Real (H-09) | El mensaje contenía el byte de escape; todavía no hay CLI que lo imprima |
| IA-06 Normalización incompleta | Real (H-07) | `["././app/pedidos.py"]` devolvía `[]` |
| IA-07 Tipos de entrada | Real (H-08) | `filtrar_envio("app/pedidos.py", ["a", "p"])` devolvía `['a', 'p']` |
| IA-08 Duplicación y docstring | Real (H-10); el «coste cuadrático» no importa con pocas rutas, pero la duplicación sí | Lectura del código: `_normalizar` se llamaba en las líneas 32 y 38 |
| IA-09 El filtro no revisa el contenido | Sospecha real, fuera de este incremento | No hay código que lea archivos; queda pendiente |
| IA-10 Enlaces simbólicos | Sospecha real, fuera de este incremento | La función no abre archivos; aplica cuando la CLI los lea |
| IA-11 Falta la CLI que llama a la función | No es un defecto del código actual | Es el siguiente incremento; queda pendiente |
| IA-12 prod.env, .envrc, .pem, .key | Real (H-06) | `filtrar_envio(["prod.env"], ["prod.env"])` devolvía la ruta |

No hubo falsos positivos completos. Dos hallazgos exageraban su impacto: IA-01 (severidad) e IA-08 (rendimiento).

**Lo que la IA no encontró:** el nombre corto 8.3 de Windows (H-03). Creé un `.env` de prueba: `dir /x` mostró
el nombre corto `ENV~1` y `cat ENV~1` devolvió el contenido del `.env`. La IA revisó las rutas equivalentes en
Windows (IA-02), pero no los nombres cortos, y `filtrar_envio(["ENV~1"], ["ENV~1"])` los dejaba pasar.

## 4. Pendientes

| Pendiente | Por qué no se corrigió todavía | Plan |
|---|---|---|
| Revisar el contenido de los archivos permitidos (IA-09) | Esta función solo decide por la ruta; todavía no hay código que lea archivos | Al implementar la lectura, buscar patrones de claves, correos y teléfonos antes de enviar |
| Enlaces simbólicos (IA-10) | Mismo motivo: la función no abre archivos | Rechazar enlaces con `Path.is_symlink()` y comprobar que el destino está dentro del repositorio |
| Integración con la CLI y la API (IA-11) | Es el siguiente incremento del proyecto | Prueba de integración que confirme que solo se envía lo que devuelve `filtrar_envio` |

**Claves expuestas:** Ninguna.
