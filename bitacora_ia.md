# Bitácora de uso de IA

Proyecto: Pruebas asistidas por IA para el módulo de pedidos
Estudiante: David Felipe Deulufeutt Cortinez
Funcionalidad: HU-10 Enviar al asistente solo los archivos de la lista permitida
Asistente usado: Claude Code (modelo Claude Opus 5.5), en modo agente, desde la aplicación de escritorio de Claude

## Entradas

### Entrada 1

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Prompt: «empezmos con la HU-10, como me recomendarias ponerle al repo». Al
  escribir el contrato, el asistente preguntó qué hacer con un archivo que no está en la lista permitida y
  no es prohibido, y sugirió omitirlo sin error.
- **Decisión:** Aceptada
- **Por qué:** El escenario 1 de HU-10 dice que «solo se envían esos archivos». Lanzar un error obligaría al
  desarrollador a limpiar la selección a mano sin ganar seguridad, porque el archivo omitido de todas formas no
  sale.
- **Verificación:** Las pruebas `test_envia_solo_los_archivos_de_la_lista_permitida` (omite `app/reportes.py`)
  y `test_nombre_parecido_a_uno_permitido_no_se_envia` pasan con la implementación.
- **Commit relacionado:** e1b6ba6 «Pruebas de la lista permitida de HU-10 (en rojo)»

### Entrada 2

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente sugirió bloquear también las variantes de `.env` (`.env.local`,
  `.env.example`), en cualquier carpeta y con cualquier combinación de mayúsculas.
- **Decisión:** Aceptada
- **Por qué:** RNF-04 exige que ningún contenido del `.env` llegue a la IA. Una variante como `.env.local` suele
  tener las mismas claves, y en Windows `.ENV` y `.env` son el mismo archivo.
- **Verificación:** La prueba parametrizada `test_variantes_de_env_tambien_se_bloquean` cubre `config/.env`,
  `.ENV`, `.env.local` y `.env.example`, y los cuatro casos pasan.
- **Commit relacionado:** e1b6ba6 «Pruebas de la lista permitida de HU-10 (en rojo)»

### Entrada 3

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente sugirió que la lista permitida aceptara patrones como `pedidos/*.py`
  en lugar de rutas exactas.
- **Decisión:** Rechazada
- **Por qué:** Con rutas exactas se sabe con precisión qué sale hacia la API, que es lo que protege RNF-04. Con un
  patrón, un archivo nuevo de la carpeta se enviaría sin que nadie lo hubiera revisado.
- **Verificación:** El contrato del README lo deja como supuesto, y
  `test_nombre_parecido_a_uno_permitido_no_se_envia` comprueba que `app/pedidos.py.bak` no coincide con
  `app/pedidos.py`.
- **Commit relacionado:** e1b6ba6 «Pruebas de la lista permitida de HU-10 (en rojo)»

### Entrada 4

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente escribió las pruebas de rutas de Windows con cadenas como
  `"app\pedidos.py"`. Al correr `pytest` apareció `SyntaxWarning: invalid escape sequence '\p'`.
- **Decisión:** Aceptada con cambios
- **Por qué:** La prueba funcionaba por casualidad: Python deja `\p` tal cual porque no es un escape válido,
  pero con otra letra, como `\n`, el valor habría cambiado sin aviso. Se cambiaron por cadenas crudas
  (`r"app\pedidos.py"`) en un commit aparte, sin tocar lo que la prueba comprueba.
- **Verificación:** Con `python -W error` el archivo de pruebas ya no da avisos, y las pruebas siguieron en rojo
  porque la función todavía no existía.
- **Commit relacionado:** 51a1051 «Corrige dos cadenas con barra invertida en las pruebas»

### Entrada 5

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Con el contrato y las pruebas como contexto, el asistente propuso la implementación
  de `filtrar_envio`: normalizar cada ruta, lanzar `ArchivoProhibidoError` si es prohibida y devolver las
  permitidas sin repetidas y en orden.
- **Decisión:** Aceptada
- **Por qué:** Cumple el contrato y respeta el diseño: es la lista permitida del comando `archivos` y no toca
  el código de la aplicación (RNF-07).
- **Verificación:** `pytest`: 12 pruebas pasan. Revisé que el error se lance antes de devolver nada, como pide
  el escenario 2 de HU-10.
- **Commit relacionado:** 92a51d2 «Implementa filtrar_envio para HU-10 (pruebas en verde)»

### Entrada 6

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Para el refactor, el asistente propuso: (1) sacar a `_normalizar` la limpieza de
  rutas repetida, (2) pasar `.env` y las extensiones de base de datos a constantes y (3) reemplazar la limpieza
  manual por `pathlib.PurePosixPath`.
- **Decisión:** Aceptada con cambios
- **Por qué:** Apliqué 1 y 2 y descarté el 3, porque un refactor no debe cambiar el comportamiento:
  `PurePosixPath` convierte `app//pedidos.py` en `app/pedidos.py`, y eso no está en el contrato.
- **Verificación:** Las 12 pruebas pasan sin modificarlas (`git diff -- tests` vacío). Comprobé en Python que
  `PurePosixPath("app//pedidos.py")` devuelve `app/pedidos.py`.
- **Commit relacionado:** c97bf66 «Refactor de filtrar_envio sin cambiar su comportamiento»

## Semana 6: revisión de código y seguridad

### Entrada 7

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Segunda revisión con un agente revisor independiente de Claude Code, que solo podía
  leer. Prompt: «Actúa como revisor de código y seguridad de un equipo Python. NO modifiques ningún archivo: solo
  lee y reporta. Contexto: el repositorio está en C:\Users\User\Escritorio\asistente-pruebas-pedido (commit
  c3066d7). Es una CLI en Python que, antes de enviar código a una API de IA externa, filtra los archivos con una
  lista permitida. Su objetivo de seguridad (RNF-04) es que ningún contenido del archivo .env ni de la base de
  datos real (unos 200 clientes) llegue a la IA. Revisa asistente/archivos.py, tests/test_archivos.py,
  .gitignore, requirements.txt, pytest.ini y README.md. Tarea: revisa el código con estos criterios: 1.
  Corrección y pruebas: ¿la función cumple el contrato del README? ¿Faltan casos límite o de abuso en las
  pruebas? 2. Diseño y legibilidad: nombres, valores mágicos, duplicación, docstrings. 3. Seguridad: inyección,
  secretos (código, historial de git, .gitignore, .env.example), contraseñas, control de acceso (¿se puede saltar
  el filtro?), dependencias (existen, son necesarias, tienen versión fijada). Formato: una tabla con Id (IA-01,
  IA-02...), archivo y línea, problema, categoría (OWASP o tipo), severidad (alta, media o baja) y corrección
  propuesta. Separa la tabla en dos partes: «Problemas seguros», los que puedes demostrar con el código, y
  «Sospechas», los que dependen de supuestos que no puedes comprobar. Para cada problema seguro incluye una
  entrada concreta que lo demuestre. Restricciones: no inventes líneas ni funciones que no existan; cita el
  número de línea real. Si un criterio no aplica, dilo con su razón. Máximo 12 hallazgos, ordenados por
  severidad. Tu respuesta final debe ser solo el informe, en español.»
- **Decisión:** Aceptada con cambios
- **Por qué:** Los 8 problemas seguros se reprodujeron, así que se aceptaron, pero IA-01 bajó de alta a media: solo
  expone datos si el archivo también está en la lista permitida. Las sospechas IA-09, IA-10 e IA-11 quedaron como
  pendientes porque dependen de la CLI que leerá los archivos, que todavía no existe.
- **Verificación:** Ejecuté en Python la entrada de cada hallazgo (por ejemplo, `papeleria.db-wal` y `.env::$DATA`
  pasaban el filtro) y las dos versiones alteradas de IA-04, que pasaban las 12 pruebas. La clasificación completa
  está en la sección 3 de [revision_seguridad.md](revision_seguridad.md).
- **Commit relacionado:** c3066d7 (commit revisado)

### Entrada 8

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** El asistente preguntó si corregir todos los hallazgos reales (IA-01 a IA-08, IA-12 y el
  nombre corto `ENV~1`) o solo los de severidad alta y media.
- **Decisión:** Aceptada: corregir todos los reales, uno por commit y con pruebas de abuso nuevas.
- **Por qué:** La rúbrica pide corregir todos los problemas reales, y cada uno se corrige con poco código. Dejar los
  de severidad baja habría dejado, por ejemplo, el `TypeError` sin control.
- **Verificación:** Después de cada commit corrí `pytest` y `ruff check .`. Al final pasan 44 pruebas (32 nuevas),
  ninguna de las 12 originales cambió y ruff no da avisos.
- **Commit relacionado:** 88344e4 a 745b5d9 (un commit por hallazgo)

### Entrada 9

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Para IA-05, el revisor propuso escribir la ruta en el mensaje con `{ruta!r}`.
- **Decisión:** Rechazada
- **Por qué:** `{ruta!r}` cambia el mensaje a `El archivo '.env' no se puede enviar`, con comillas, y haría fallar
  `test_seleccion_con_env_no_envia_nada_e_indica_el_archivo`. Para que pasara habría que modificar una prueba
  existente, cosa que las reglas prohíben. En su lugar, los caracteres de control se muestran como `?`, y el
  mensaje de las rutas normales no cambia.
- **Verificación:** La prueba nueva `test_mensaje_de_error_no_incluye_caracteres_de_control` comprueba el mensaje
  exacto, y la prueba de `.env` sigue pasando sin cambios.
- **Commit relacionado:** bd7d16f «Quita caracteres de control del mensaje de error (IA-05)»

### Entrada 10

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Las correcciones las hizo Claude Code como agente, en la rama propia
  `revision/semana6`, con una instrucción delimitada: corregir los hallazgos reales de la revisión, uno por
  commit, sin modificar las pruebas existentes y con pruebas de abuso nuevas.
- **Decisión:** Aceptada con cambios
- **Por qué:** En la revisión del diff apareció un defecto del propio agente: la prueba de IA-05 tenía un byte de
  escape real dentro del archivo, en lugar del texto `\x1b`. Funcionaba, pero no se podía leer ni revisar. Se
  corrigió en ese mismo commit, antes de subirlo. El resto del diff cumplía la instrucción: un commit por hallazgo
  y ninguna de las 12 pruebas originales modificada.
- **Verificación:** Revisé el diff de `main..revision/semana6` antes de integrarlo. Con `grep` confirmé que no quedan
  bytes de escape en las pruebas. Cloné la rama en una carpeta limpia y corrí los comandos del README: instalación,
  `pytest` (44 pruebas pasan), `ruff check .` (sin avisos) y `pip-audit` (sin vulnerabilidades).
- **Commit relacionado:** merge de `revision/semana6` en `main`

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 4 |
| Aceptadas con cambios | 4 |
| Rechazadas | 2 |

## Errores que atraparon las pruebas

La implementación generada pasó las 12 pruebas al primer intento, así que ninguna prueba falló por un error de
la función. El error lo atrapó la ejecución de `pytest` en el código de las propias pruebas, que también generó el
asistente: dos rutas de Windows escritas como `"app\pedidos.py"` producían `SyntaxWarning: invalid escape
sequence '\p'`. Funcionaban por casualidad. Las corregí con cadenas crudas en un commit aparte (entrada 4), sin
cambiar lo que comprueban.

## Reflexión final

El asistente me ayudó más al convertir HU-10 en un contrato con casos límite que yo no había pensado, como
`.ENV` en mayúsculas, `.env.example` o una base de datos puesta por error en la lista permitida. También me
mostró que las decisiones de diseño aparecen antes del código: tuve que elegir si un archivo fuera de la lista
se omite o da error. Las pruebas no atraparon errores en la función, pero `pytest` sí mostró un defecto en las
pruebas generadas, y eso me enseñó a no ignorar los avisos aunque todo esté en verde. En el refactor rechacé
`pathlib` porque cambiaba el comportamiento. En la próxima funcionalidad escribiría yo al menos un caso de
error antes de pedirle pruebas al asistente, para comparar lo que propone con lo que yo esperaba.

## Errores que atraparon las pruebas en la semana 6

Las pruebas nuevas de IA-04 atraparon dos versiones defectuosas de `filtrar_envio`, que pasaban las 12 pruebas de
la semana 5. Con una función que solo bloqueaba `.db`, fallaron 7 pruebas: `papeleria.db-wal`, `.sqlite` y
`.sqlite3`. Con una función que no normalizaba la lista permitida, falló 1:
`test_lista_permitida_escrita_con_barra_invertida_tambien_se_normaliza`. Esto mostró que tener 12 pruebas en verde
no bastaba: también había que probar que fallan cuando el código está mal.

## Reflexión de la semana 6

La revisión con IA encontró problemas que mis 12 pruebas no veían, como los archivos `-wal` de SQLite, pero los
tuve que reproducir uno por uno antes de aceptarlos, y uno exageraba su severidad. Lo más útil fue buscar lo que
la IA no vio: el nombre corto `ENV~1` de Windows, que comprobé con un `.env` de prueba. También aprendí que el
agente comete errores al corregir, como el byte de escape en una prueba, y que por eso hay que revisar su diff
antes de integrarlo.
