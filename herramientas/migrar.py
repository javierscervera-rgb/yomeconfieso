#!/usr/bin/env python3
"""Migración única: convierte los fragmentos de IONOS (carpeta original/)
en páginas completas con cabecera, menú y pie comunes.
Después de ejecutarlo, las páginas generadas son la fuente que se edita."""
import re, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(RAIZ, "original")

PAGINAS = {
    # slug: (título <title>, descripción, ancha)
    "inicio": ("yomeconfieso · Tu guía para confesarte", "Tu guía paso a paso para el examen de conciencia y la confesión.", False),
    "0-intro": ("El sacramento de la misericordia · yomeconfieso", "Qué es el sacramento de la Confesión.", False),
    "0-dudas": ("Dudas sobre la Confesión · yomeconfieso", "Respuestas a las dudas más frecuentes sobre el sacramento de la Confesión.", False),
    "1-prepara": ("Prepara tu confesión · yomeconfieso", "Vídeos y ayudas para preparar la Confesión.", False),
    "2-examen": ("Examen de conciencia para adultos · yomeconfieso", "Examen de conciencia interactivo para adultos.", True),
    "2-examen-jovenes": ("Examen de conciencia para jóvenes · yomeconfieso", "Examen de conciencia interactivo para jóvenes de 15 a 30 años.", True),
    "2-examen-primaria": ("Examen de conciencia para chicos/as · yomeconfieso", "Examen de conciencia interactivo para chicos y chicas de 10 a 15 años.", True),
    "3-preguntas": ("Preguntas del examen · yomeconfieso", "Preguntas del examen de conciencia.", False),
    "3-preguntas-jovenes": ("Preguntas del examen · yomeconfieso", "Preguntas del examen de conciencia para jóvenes.", False),
    "3-preguntas-primaria": ("Preguntas del examen · yomeconfieso", "Preguntas del examen de conciencia para chicos y chicas.", False),
    "4-dos-cosas": ("Dos cosas antes de confesarte · yomeconfieso", "Antes de confesarte.", False),
    "5-ayudas": ("Ayudas antes de confesarte · yomeconfieso", "Oraciones, vídeo y parroquias cercanas.", False),
    "6-paso-a-paso": ("La confesión paso a paso · yomeconfieso", "Guía para el momento de la confesión.", False),
    "7-final": ("Terminando · yomeconfieso", "Después de la confesión.", False),
    "contacto": ("Contacto · yomeconfieso", "Escríbenos.", False),
}

MENU = [("Inicio", "/", "inicio"), ("Dudas", "/0-dudas/", "0-dudas"), ("Contacto", "/contacto/", "contacto")]

# ---------- CSS: prefijar todos los selectores con .pagina ----------
def prefijar_css(css):
    css = re.sub(r"@import\s+url\([^)]*\)[^;]*;", "", css)
    out, i = [], 0
    while i < len(css):
        j = css.find("{", i)
        if j < 0:
            out.append(css[i:]); break
        sel = css[i:j].strip()
        # buscar llave de cierre equilibrada
        depth, k = 1, j + 1
        while depth and k < len(css):
            if css[k] == "{": depth += 1
            elif css[k] == "}": depth -= 1
            k += 1
        cuerpo = css[j + 1:k - 1]
        coment = ""
        m = re.match(r"^((?:/\*.*?\*/\s*)*)(.*)$", sel, re.S)
        if m: coment, sel = m.group(1), m.group(2).strip()
        if sel.startswith("@media") or sel.startswith("@supports"):
            out.append(f"{coment}{sel} {{{prefijar_css(cuerpo)}}}\n")
        elif sel.startswith("@"):
            out.append(f"{coment}{sel} {{{cuerpo}}}\n")
        else:
            partes = [p.strip() for p in sel.split(",") if p.strip()]
            nuevas = []
            for p in partes:
                if p in ("body", "html", ":root"):
                    continue  # el fondo y la tipografía los pone la plantilla
                if re.match(r"^(html|body)\b", p):
                    p = re.sub(r"^(html|body)\s*", "", p)
                nuevas.append(".pagina " + p if p != "*" else ".pagina *")
            if sel.strip() == ":root":
                out.append(f"{coment}.pagina {{{cuerpo}}}\n")
            elif nuevas:
                out.append(f"{coment}{', '.join(nuevas)} {{{cuerpo}}}\n")
        i = k
    return "".join(out)

def limpiar_codigo(html):
    html = re.sub(r"<meta[^>]*>\s*", "", html)
    html = re.sub(r"<title>.*?</title>\s*", "", html, flags=re.S)
    html = re.sub(r"<style>(.*?)</style>", lambda m: "<style>\n" + prefijar_css(m.group(1)) + "</style>", html, flags=re.S)
    return html.strip()

def limpiar_texto(html):
    html = re.sub(r'\s*class="[^"]*"', "", html)
    html = re.sub(r'\s*style="font-family:[^"]*"', "", html)
    html = re.sub(r"<span>(.*?)</span>", r"\1", html, flags=re.S)
    html = re.sub(r"^<div>|</div>$", "", html.strip())
    return html.strip()

def urls(html):
    html = re.sub(r"https?://(www\.)?yomeconfieso\.es/", "/", html)
    html = html.replace("https://n2005905.websitebuilder.online/", "/")
    # enlaces sin barra final -> con barra
    html = re.sub(r'(["\'])/(\d-[a-z0-9-]+|contacto)(["\'])', r"\1/\2/\3", html)
    return html

def trocear(slug):
    txt = open(os.path.join(ORIG, slug + ".html"), encoding="utf-8").read()
    bloques = re.split(r"\n<!-- ===== (HEADING|TEXT|CODE|IMG) ===== -->\n", txt)
    res = []
    for n in range(1, len(bloques), 2):
        res.append((bloques[n], bloques[n + 1].strip()))
    return res

def cabecera_html(slug, portada=False):
    activo = ' class="activo"'
    items = "".join(
        f'<a href="{href}"{activo if s == slug else ""}>{nombre}</a>' for nombre, href, s in MENU)
    marca = "" if portada else '<a class="yc-marca" href="/" aria-label="Inicio"><img src="/img/logo.png" alt="yo me confieso"></a>'
    if portada:
        marca = "<span></span>"
    return f'<header class="yc-cabecera">{marca}<nav class="yc-menu">{items}</nav></header>'

def documento(slug, cuerpo, portada=False):
    titulo, desc, _ = PAGINAS[slug]
    canon = "https://www.yomeconfieso.es/" + ("" if slug == "inicio" else slug + "/")
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://www.yomeconfieso.es/img/abrazo.jpg">
<meta property="og:locale" content="es_ES">
<link rel="icon" href="/favicon.png">
<link rel="apple-touch-icon" href="/img/icono-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Raleway:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/estilo.css">
</head>
<body class="yc{' portada' if portada else ''}">
{cabecera_html(slug, portada)}
<main class="yc-principal">
{cuerpo}
</main>
<footer class="yc-pie">yomeconfieso.es · <a href="/0-dudas/">Dudas</a> · <a href="/contacto/">Contacto</a></footer>
</body>
</html>
"""

# ---------- arreglos concretos por página ----------
def arreglos(slug, codigo):
    if slug == "2-examen":
        codigo = codigo.replace("'Bulling'", "'Bullying'")
    if slug.startswith("2-examen"):
        # En escritorio el cuadro debe ser estrecho para poder deslizar las cajas,
        # y se puede arrastrar con el ratón o la rueda.
        codigo = codigo.replace("</style>", """
.pagina .scroll-container { max-width: 440px; cursor: grab; }
.pagina .scroll-container.arrastrando { cursor: grabbing; }
</style>""", 1)
        codigo = codigo.replace("requestAnimationFrame(animate);\n        }", """requestAnimationFrame(animate);

            // Ratón: arrastrar o usar la rueda para deslizar las cajas
            let arrastre = null;
            scrollCont.addEventListener('pointerdown', e => {
                if (e.pointerType !== 'mouse') return;
                arrastre = { x: e.clientX, left: scrollCont.scrollLeft };
                scrollCont.classList.add('arrastrando');
            });
            window.addEventListener('pointermove', e => {
                if (arrastre) scrollCont.scrollLeft = arrastre.left - (e.clientX - arrastre.x);
            });
            window.addEventListener('pointerup', () => {
                arrastre = null;
                scrollCont.classList.remove('arrastrando');
            });
            scrollCont.addEventListener('wheel', e => {
                if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
                    scrollCont.scrollLeft += e.deltaY;
                    e.preventDefault();
                }
            }, { passive: false });
        }""", 1)
        assert "arrastre" in codigo, slug
        # al empezar, colocar el juego a pantalla completa (si no, las cajas quedan por debajo)
        codigo = codigo.replace("initApp();", "document.querySelector('.main-container').scrollIntoView({ block: 'center' });\n                initApp();", 1)
        codigo = codigo.replace(".pagina .start-subtitle {\n            font-size: 1rem;", ".pagina .start-subtitle {\n            font-size: 1.1rem;")
    if slug.startswith("3-preguntas"):
        codigo = codigo.replace("te confesaros", "te confesaste")
    if slug == "6-paso-a-paso":
        codigo = re.sub(r'<script src="https://cdn\.tailwindcss\.com"></script>\s*', "", codigo)
        codigo = codigo.replace("</style>", """
.pagina .continue-btn { border: none; cursor: pointer; font-size: 1.125rem; }
.pagina .text-green-700 { color: #15803d; }
.pagina .font-medium { font-weight: 500; }
.pagina .mt-6 { margin-top: 1.5rem; }
.pagina .chat-body { min-height: 60vh; }
</style>""", 1)
    if slug == "inicio":
        codigo = re.sub(r"display: none;\s*/\* Oculto por defecto \(escritorio\) \*/", "display: flex;", codigo)
        codigo = re.sub(r"grid-template-rows: repeat\(3, auto\);", "", codigo)
        assert "Oculto por defecto" not in codigo
        codigo = codigo.replace("</style>", """
@media (min-width: 768px) { .pagina .contenedor { grid-template-columns: repeat(3, 1fr); } }
.pagina .contenedor { margin: 0 auto; }
</style>""", 1)
    if slug in ("0-intro", "4-dos-cosas"):
        # que los párrafos aparezcan también en pantallas grandes sin tener que hacer scroll
        codigo = codigo.replace('rootMargin:"-67% 0px -10% 0px"', 'rootMargin:"0px 0px -15% 0px"')
    if slug in ("0-intro", "7-final"):
        codigo = re.sub(r'(href="/[^"]*")\s+target="_blank"', r"\1", codigo)
    return codigo

def construir(slug):
    _, _, ancha = PAGINAS[slug]
    bloques = trocear(slug)
    titulares, textos_antes, codigo, textos_despues = [], [], "", []
    for tipo, contenido in bloques:
        if tipo == "HEADING":
            titulares.append(limpiar_texto(contenido))
        elif tipo == "TEXT":
            t = limpiar_texto(contenido)
            if re.fullmatch(r"<p>\.?</p>", t):  # separadores vacíos de IONOS
                continue
            (textos_despues if codigo else textos_antes).append(t)
        elif tipo == "CODE":
            if "aviso-dispositivo" in contenido:  # aviso «solo móvil»: ya no hace falta
                continue
            codigo = urls(arreglos(slug, limpiar_codigo(contenido)))
    partes = []
    if slug == "inicio":
        partes.append('<section class="yc-hero"><h1><img src="/img/logo.png" alt="Yo me confieso"></h1>'
                      '<p class="yc-lema">Tu guía paso a paso para el examen de conciencia y la confesión</p></section>')
    if titulares:
        h = titulares[0]
        h = re.sub(r"^<h[12][^>]*>|</h[12]>$", "", h)
        sub = ""
        if len(titulares) > 1:
            sub = '<p class="yc-sub">' + re.sub(r"</?h[12][^>]*>", "", titulares[1]) + "</p>"
        partes.append(f'<header class="yc-titular"><h1>{h}</h1>{sub}</header>')
    for t in textos_antes:
        clase = "yc-texto yc-aviso" if "NO SUSTITUYE" in t else "yc-texto"
        partes.append(f'<div class="{clase}">{urls(t)}</div>')
    if codigo:
        partes.append(f'<div class="pagina{" ancha" if ancha else ""}">\n{codigo}\n</div>')
    for t in textos_despues:
        partes.append(f'<div class="yc-texto">{urls(t)}</div>')
    if slug == "5-ayudas":
        partes.append('<a class="yc-boton" href="/6-paso-a-paso/">Estoy preparado</a>')
    if slug == "0-dudas":
        partes.append('<a class="yc-boton" href="/">Volver al inicio</a>')
    html = documento(slug, "\n".join(partes), portada=(slug == "inicio"))
    for mal, bien in [("te confesaros", "te confesaste"), ("cercansa", "cercanas"), ("pero pero", "pero"), ("momento en vayas", "momento en que vayas")]:
        html = html.replace(mal, bien)
    # rutas relativas: funcionan igual en el dominio propio y en la vista previa de github.io
    pre = "./" if slug == "inicio" else "../"
    html = re.sub(r'((?:href|src|data-url)=|location\.href\s*=\s*)(["\'])/(?!/)', lambda m: m.group(1) + m.group(2) + pre, html)
    ruta = os.path.join(RAIZ, "index.html" if slug == "inicio" else os.path.join(slug, "index.html"))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    open(ruta, "w", encoding="utf-8").write(html)
    print("ok", slug, len(html))

if __name__ == "__main__":
    for s in (sys.argv[1:] or PAGINAS):
        construir(s)
