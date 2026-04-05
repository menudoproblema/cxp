# Catálogo de Browser Automation

> Estado actual: familia abstracta de compatibilidad para runtimes de automatización de navegador.

## Interfaz
Este catálogo documenta la familia abstracta `browser/automation`.

No define capabilities concretas ni se usa como objetivo directo de validación.
Su papel es permitir que un consumidor exprese una necesidad genérica de
automatización de navegador y que un catálogo concreto declare compatibilidad
mediante `satisfies_interfaces`.

## Uso Esperado
- Pedir compatibilidad general de automatización de navegador en el handshake.
- Permitir que contratos concretos como `browser/playwright` satisfagan esa familia.
- Mantener separado el vocabulario abstracto de la semántica concreta de una herramienta.

## Catálogos Concretos Actuales
- `browser/playwright`
