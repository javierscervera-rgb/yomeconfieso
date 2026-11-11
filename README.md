# yomeconfieso

Web [www.yomeconfieso.es](https://www.yomeconfieso.es): guía para el examen de conciencia y la confesión.

## Estructura

- `index.html` — portada
- `<sección>/index.html` — cada página (`0-intro`, `0-dudas`, `1-prepara`, `2-examen*`, `3-preguntas*`, `4-dos-cosas`, `5-ayudas`, `6-paso-a-paso`, `7-final`, `contacto`)
- `css/estilo.css` — cabecera, menú, fondo y tipografía comunes
- `img/` — cuadro del abrazo (fondo), logo e icono
- `original/` — copia de los fragmentos de código tal como estaban en IONOS (solo de referencia)
- `herramientas/migrar.py` — script usado una vez para pasar de IONOS a esta web

Las páginas de `<sección>/index.html` son ya la fuente: se editan directamente.
El estilo propio de cada página va dentro de su `<div class="pagina">`, con todos los selectores prefijados por `.pagina` para no afectar a la cabecera ni al pie.

## Recorrido

Portada → Examen (adultos / jóvenes / chicos) → Preguntas → Dos cosas → Ayudas → Paso a paso → Final.
Los datos del examen pasan de una página a otra con `localStorage` en el navegador; no se envía nada a ningún servidor.
