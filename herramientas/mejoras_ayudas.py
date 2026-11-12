#!/usr/bin/env python3
"""Ayudas: sustituye el buscador de parroquias por js/parroquias.js (solo católicas, más rápido)."""
import os, re, hashlib
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = hashlib.md5(open(os.path.join(RAIZ, "js", "parroquias.js"), "rb").read()).hexdigest()[:8]
ruta = os.path.join(RAIZ, "5-ayudas", "index.html")
s = open(ruta, encoding="utf-8").read()
if "parroquias.js" not in s:
    s, n = re.subn(r"\nlet userLat, userLon;.*?\nfunction irAGoogleMaps\(lat, lon\) \{.*?\n\}\n", "\n", s, flags=re.S)
    assert n == 1, "no se encontró el buscador antiguo"
    s = s.replace("</body>", f'<script src="../js/parroquias.js?v={V}"></script>\n</body>', 1)
    open(ruta, "w", encoding="utf-8").write(s)
    print("ok 5-ayudas")
