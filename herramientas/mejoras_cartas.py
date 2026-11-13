#!/usr/bin/env python3
"""Páginas de examen: texto de presentación + «Comenzar», ventana para elegir sistema,
y el juego (cartas o caída) dentro de una ventana grande. Al terminar, la ventana se
funde y aparece en la página el botón «Iniciar chat»."""
import os, re, json, hashlib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_JS = hashlib.md5(open(os.path.join(RAIZ, "js", "cartas.js"), "rb").read()).hexdigest()[:8]

TEXTOS = {
    "2-examen": ("Adultos", [
        "El examen de conciencia es mirar con calma tu vida a la luz del amor de Dios para reconocer en qué le has fallado a Él, a los demás y a ti mismo desde tu última confesión.",
        "Primero colocarás unas palabras según cuánto han estado presentes en tu vida: <strong>mucho, regular, poco o nada</strong>. Con lo que marques te prepararemos después unas preguntas concretas.",
        "No pienses demasiado: lo importante es ser sincero. Tus respuestas se quedan solo en este dispositivo.",
    ]),
    "2-examen-jovenes": ("Jóvenes", [
        "El examen de conciencia es parar un momento y mirar tu vida con los ojos de Dios: qué ha ido bien y en qué le has fallado a Él, a los demás o a ti mismo desde tu última confesión.",
        "Primero colocarás unas palabras según cuánto han estado presentes en tu vida: <strong>mucho, regular, poco o nada</strong>. Con lo que marques te prepararemos después unas preguntas pensadas para ti.",
        "No le des muchas vueltas: lo importante es ser sincero. Tus respuestas se quedan solo en tu móvil.",
    ]),
    "2-examen-primaria": ("Chicos y chicas", [
        "El examen de conciencia es pensar con calma en lo que has hecho, para darte cuenta de en qué no te has portado bien con Dios, con los demás o contigo.",
        "Primero vas a colocar unas palabras según cuánto te pasan: <strong>mucho, regular, poco o nada</strong>. Después te haré unas preguntas sobre lo que hayas elegido.",
        "No pienses mucho, solo sé sincero. Nadie más va a ver tus respuestas.",
    ]),
}

for slug, (publico, parrafos) in TEXTOS.items():
    ruta = os.path.join(RAIZ, slug, "index.html")
    s = open(ruta, encoding="utf-8").read()
    if 'id="juegoModal"' in s:
        print("ya aplicado", slug); continue
    lista = re.search(r"const wordList\s*=\s*\[(.*?)\];", s, re.S).group(1)
    palabras = re.findall(r"""['"]([^'"]+)['"]""", lista)
    destino = re.search(r"""window\.location\.href = ["'](\.\./3-preguntas[^"']*)["']""", s).group(1)

    intro = ('<div class="yc-texto yc-lectura" id="examenIntro">' + "".join(f"<p>{p}</p>" for p in parrafos) +
             '<button type="button" class="yc-boton yc-boton-izq" id="empezarExamen">Comenzar</button></div>\n'
             '<div class="yc-texto examen-fin" id="finExamen" hidden>'
             '<p class="examen-fin-titulo">¡Hecho! Ya has colocado todas las palabras.</p>'
             '<p>Ahora vienen unas preguntas concretas sobre lo que has marcado.</p>'
             f'<a class="yc-boton yc-boton-izq" href="{destino}">Iniciar chat</a>'
             '<button type="button" class="examen-repetir" id="repetirExamen">Volver a empezar</button></div>\n')
    s = s.replace('<div class="pagina ancha">', intro + '<div class="pagina ancha">', 1)

    # el juego dentro de una ventana grande
    s = s.replace("<!-- Pantalla de inicio -->",
                  '<div id="juegoModal" class="juego-modal" hidden role="dialog" aria-modal="true" aria-label="Examen de conciencia">\n'
                  f'      <div class="juego-modal-cabecera"><span>Examen de conciencia · {publico}</span>'
                  '<button type="button" id="cerrarJuego" class="juego-cerrar" aria-label="Cerrar">'
                  '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>\n'
                  '      <div class="juego-modal-cuerpo">\n'
                  '    <div id="cartas" class="cartas" hidden></div>\n\n    <!-- Pantalla de inicio -->', 1)
    s, n = re.subn(r'(<button id="continueBtn">INICIAR CHAT</button>\s*</div>)', r'\1\n      </div>\n    </div>', s, count=1)
    assert n == 1, slug
    s = s.replace('<div id="startScreen">', '<div id="startScreen" style="display:none">', 1)
    # al terminar el juego de caída: cerrar la ventana en lugar del botón flotante
    s = s.replace("continueBtn.style.display = 'block';",
                  "if (window.finExamen) { window.finExamen(); } else { continueBtn.style.display = 'block'; }", 1)
    # ya no hace falta recolocar la página al empezar
    s = s.replace("document.querySelector('.main-container').scrollIntoView({ block: 'center' });\n", "", 1)
    s = s.replace("</body>",
                  f"<script>window.PALABRAS_EXAMEN = {json.dumps(palabras, ensure_ascii=False)};\n"
                  f"window.DESTINO_PREGUNTAS = {json.dumps(destino)};</script>\n"
                  f'<script src="../js/cartas.js?v={VERSION_JS}"></script>\n</body>', 1)
    assert 'id="cartas"' in s and "finExamen" in s and 'style="display:none"' in s
    open(ruta, "w", encoding="utf-8").write(s)
    print("ok", slug, len(palabras), destino)
