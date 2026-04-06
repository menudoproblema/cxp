# Catálogo de Playwright Browser

> Estado actual: catálogo provisional. El vocabulario ya es útil para interoperabilidad, pero sigue siendo revisable si cambian los consumidores reales.

## Interfaz
Este catálogo define el vocabulario canónico de capabilities para la interfaz
`browser/playwright`.

Satisface la familia abstracta `browser/automation`.

## Capabilities Canónicas
- `browser_lifecycle`: apertura y cierre de sesiones de navegador.
- `context_management`: creación y cierre de contextos aislados.
- `page_navigation`: navegación, recarga e historial.
- `locator_resolution`: resolución y refinado de locators antes de actuar.
- `dom_interaction`: acciones directas sobre elementos del DOM.
- `wait_conditions`: esperas explícitas sobre selector, URL o respuesta.
- `script_evaluation`: evaluación de script en página o elemento.
- `network_observation`: observación de requests y responses durante la automatización.
- `screenshot_capture`: captura de screenshots de página o elemento.
- `dialog_handling`: gestión de dialogs del navegador.

## Tiers de Conformidad
### Core
- `browser_lifecycle`
- `context_management`
- `page_navigation`
- `locator_resolution`
- `dom_interaction`
- `wait_conditions`

`core` representa automatización interactiva básica con control de sesión,
navegación, resolución de elementos y sincronización explícita.

### Observable
- `browser_lifecycle`
- `context_management`
- `page_navigation`
- `locator_resolution`
- `dom_interaction`
- `wait_conditions`
- `script_evaluation`
- `network_observation`
- `screenshot_capture`
- `dialog_handling`

`observable` amplía `core` con observabilidad de red, ejecución de script,
captura visual y gestión de dialogs.

## Operaciones Canónicas
- `browser_lifecycle`: `browser.launch`, `browser.close`
- `context_management`: `context.create`, `context.close`
- `page_navigation`: `page.goto`, `page.reload`, `page.go_back`
- `locator_resolution`: `locator.query`, `locator.filter`
- `dom_interaction`: `element.click`, `element.fill`, `element.press`, `element.select_option`
- `wait_conditions`: `wait.for_selector`, `wait.for_url`, `wait.for_response`
- `script_evaluation`: `page.evaluate`, `element.evaluate`
- `network_observation`: `network.request.observe`, `network.response.observe`
- `screenshot_capture`: `page.screenshot`, `element.screenshot`
- `dialog_handling`: `dialog.accept`, `dialog.dismiss`

## Perfiles Reutilizables
- `playwright-core`: exige ciclo de vida, contextos, navegación, locators, interacción DOM y waits.
- `playwright-observable`: extiende `playwright-core` y exige además evaluación de script, observación de red, screenshots y dialogs.

## Telemetría Canónica
La telemetría de `browser/playwright` se declara por capability y se concentra
en las señales mínimas con valor interoperable para un orquestador:

- `browser_lifecycle`: `browser.launch`, `browser.close`, `browser.launch.duration`, `browser.close.duration`, `browser.session.launched`, `browser.session.launch_failed`, `browser.session.closed`
- `context_management`: `browser.context.create`, `browser.context.close`, `browser.context.create.duration`, `browser.context.close.duration`, `browser.context.created`, `browser.context.create_failed`, `browser.context.closed`
- `page_navigation`: `browser.page.navigate`, `browser.navigation.duration`, `browser.navigation.completed`
- `locator_resolution`: `browser.locator.resolve`, `browser.locator.retry_count`, `browser.locator.resolved`
- `dom_interaction`: `browser.action`, `browser.action.duration`, `browser.action.completed`
- `wait_conditions`: `browser.wait`, `browser.wait.duration`, `browser.wait.completed`, `browser.wait.timed_out`
- `script_evaluation`: `browser.script.evaluate`, `browser.script.duration`, `browser.script.completed`
- `network_observation`: `browser.request.observe`, `browser.response.observe`, `browser.request.duration`, `browser.response.duration`, `browser.request.observed`, `browser.response.observed`, `browser.request.failed`, `browser.response.failed`
- `screenshot_capture`: `browser.screenshot.capture`, `browser.screenshot.bytes`, `browser.screenshot.captured`
- `dialog_handling`: `browser.dialog.handle`, `browser.dialog.duration`, `browser.dialog.opened`, `browser.dialog.handled`

## Campos Requeridos Más Útiles
Los campos mínimos compartidos más relevantes son:

- `browser.engine`
- `browser.context.id`
- `browser.page.id`
- `browser.outcome`

Y las capabilities especializadas añaden contexto propio:

- `browser_lifecycle`: `browser.headless`
- `context_management`: `browser.context.id`
- `page_navigation`: `browser.url.host`, `browser.url.path_template`
- `locator_resolution`: `browser.locator.kind`
- `dom_interaction`: `browser.action.name`, `browser.locator.kind`
- `wait_conditions`: `browser.wait.condition`
- `script_evaluation`: `browser.script.kind`
- `network_observation`: `browser.network.phase`, `browser.request.url.host`
- `screenshot_capture`: `browser.screenshot.target`
- `dialog_handling`: `browser.dialog.type`

## Regla de Diseño
El catálogo no intenta modelar toda la API de Playwright.

La intención es fijar un vocabulario estable y pequeño para:

- negociación interoperable;
- trazabilidad de acciones de navegador;
- razonamiento por parte de orquestadores y agentes.

Los detalles específicos del provider deben seguir viviendo en metadata
propietaria o en señales adicionales fuera del vocabulario canónico.

## Flujo de Consumo Recomendado
Un consumidor de `browser/playwright` suele:

1. elegir `playwright-core` cuando solo necesita automatización interactiva básica;
2. elegir `playwright-observable` cuando además necesita inspección de red, capturas o evaluación de script;
3. validar snapshots y telemetría solo contra el perfil realmente necesario.
