# yomeconfieso

Web [www.yomeconfieso.es](https://www.yomeconfieso.es): guía para el examen de conciencia y la confesión.

## Estructura

- `index.html` — portada
- `saber-mas/` — antes de empezar: qué es la confesión, sus cinco partes, dudas y vídeos
- Las cinco partes de la confesión:
  1. Examen de conciencia — `2-examen*/` (juego de selección o selección de cartas) y `3-preguntas*/`
  2. Dolor de los pecados — `dolor/`
  3. Propósito de la enmienda — `proposito/`
  4. Decir los pecados al confesor — `5-ayudas/` (antes de entrar) y `6-paso-a-paso/`
  5. Cumplir la penitencia — `7-final/`
- `contacto/`
- `0-intro/`, `0-dudas/`, `1-prepara/`, `4-dos-cosas/` — redirecciones a las páginas nuevas
- `css/estilo.css` — diseño común · `js/` — cartas, parroquias y funciones comunes
- `original/` — copia del código de IONOS · `herramientas/` — scripts de construcción

Para regenerar todo: `./herramientas/construir.sh` (parte de `original/` y aplica las mejoras en orden).

## Recorrido

Los datos del examen pasan de una página a otra con `localStorage` en el navegador; no se envía nada a ningún servidor.
