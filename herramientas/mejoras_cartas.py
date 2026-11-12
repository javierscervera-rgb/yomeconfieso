#!/usr/bin/env python3
"""Añade a las páginas de examen la ventana para elegir sistema y la selección de cartas (js/cartas.js)."""
import os, re, json, hashlib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_JS = hashlib.md5(open(os.path.join(RAIZ, "js", "cartas.js"), "rb").read()).hexdigest()[:8]

for slug in ("2-examen", "2-examen-jovenes", "2-examen-primaria"):
    ruta = os.path.join(RAIZ, slug, "index.html")
    s = open(ruta, encoding="utf-8").read()
    if 'id="cartas"' in s:
        print("ya aplicado", slug); continue
    lista = re.search(r"const wordList\s*=\s*\[(.*?)\];", s, re.S).group(1)
    palabras = re.findall(r"""['"]([^'"]+)['"]""", lista)
    destino = re.search(r"""window\.location\.href = ["'](\.\./3-preguntas[^"']*)["']""", s).group(1)
    s = s.replace('<div id="startScreen">', '<div id="startScreen" style="display:none">', 1)
    s = s.replace("<!-- Pantalla de inicio -->",
                  '<button type="button" id="cambiarSistema" class="cambiar-sistema">Cambiar de sistema</button>\n'
                  '    <div id="cartas" class="cartas" hidden></div>\n\n    <!-- Pantalla de inicio -->', 1)
    s = s.replace("</body>",
                  f"<script>window.PALABRAS_EXAMEN = {json.dumps(palabras, ensure_ascii=False)};\n"
                  f"window.DESTINO_PREGUNTAS = {json.dumps(destino)};</script>\n"
                  f'<script src="../js/cartas.js?v={VERSION_JS}"></script>\n</body>', 1)
    assert 'id="cartas"' in s and "PALABRAS_EXAMEN" in s and 'style="display:none"' in s
    open(ruta, "w", encoding="utf-8").write(s)
    print("ok", slug, len(palabras), destino)
