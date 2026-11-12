#!/bin/sh
# Regenera todas las páginas a partir de original/ y aplica las mejoras en orden.
set -e
cd "$(dirname "$0")/.."
python3 herramientas/migrar.py
python3 herramientas/mejoras_juego.py
python3 herramientas/mejoras_chat.py
python3 herramientas/mejoras_cartas.py
