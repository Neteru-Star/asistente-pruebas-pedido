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

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 3 |
| Aceptadas con cambios | 2 |
| Rechazadas | 1 |

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
