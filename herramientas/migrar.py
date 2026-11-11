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

PASOS = [  # (número, nombre, slug base)
    (0, "Introducción", "0-intro"),
    (1, "Prepara", "1-prepara"),
    (2, "Examen", "2-examen"),
    (3, "Preguntas", "3-preguntas"),
    (4, "Arrepentimiento", "4-dos-cosas"),
    (5, "Ayudas", "5-ayudas"),
    (6, "Paso a paso", "6-paso-a-paso"),
    (7, "Final", "7-final"),
]

TITULOS = {  # título, subtítulo
    "0-intro": ("El sacramento de la misericordia", "¿Sabes qué es?"),
    "0-dudas": ("Algunas dudas sobre la confesión", ""),
    "1-prepara": ("Prepara tu confesión", ""),
    "2-examen": ("Examen de conciencia", "Para adultos"),
    "2-examen-jovenes": ("Examen de conciencia", "Para jóvenes"),
    "2-examen-primaria": ("Examen de conciencia", "Para chicos y chicas"),
    "3-preguntas": ("Algunas preguntas preparadas para ti", ""),
    "3-preguntas-jovenes": ("Algunas preguntas para jóvenes como tú", ""),
    "3-preguntas-primaria": ("Algunas preguntas para chicos y chicas como tú", ""),
    "4-dos-cosas": ("Dos cosas antes de confesarte", ""),
    "5-ayudas": ("Algunas ayudas antes de confesarte", ""),
    "6-paso-a-paso": ("La confesión paso a paso", ""),
    "7-final": ("Terminando…", ""),
    "contacto": ("¿Quieres decirme algo?", ""),
}

ICONO_FLECHA = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

def variante(slug):
    for v in ("-jovenes", "-primaria"):
        if slug.endswith(v):
            return v
    return ""

def paso_de(slug):
    for n, nombre, base in PASOS:
        if slug == base or slug.startswith(base + "-"):
            return n, nombre
    return None, None

def href_paso(base, slug):
    v = variante(slug)
    if base in ("2-examen", "3-preguntas") and v:
        return f"/{base}{v}/"
    return f"/{base}/"

def camino_html(slug):
    actual, _ = paso_de(slug)
    items = []
    for n, nombre, base in PASOS:
        clase = ' class="activo" aria-current="page"' if n == actual else ""
        items.append(f'<a href="{href_paso(base, slug)}"{clase}><span>{n}</span>{nombre}</a>')
    return "".join(items)

MENU_ENLACES = [("Inicio", "/"), ("Dudas", "/0-dudas/"), ("Contacto", "/contacto/")]

def menu_html(slug):
    activo = {"inicio": "/", "0-dudas": "/0-dudas/", "contacto": "/contacto/"}.get(slug)
    return "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == activo else ""}>{n}</a>'.replace('\\"', '"')
        for n, h in MENU_ENLACES)

def cabecera_pagina(slug):
    n, nombre = paso_de(slug)
    if n is not None:
        barras = "".join(f'<span{" class=\"hecho\"" if i <= n else ""}></span>'.replace('\\"', '"') for i in range(8))
        etiqueta = f'Paso {n} · {nombre}'
        progreso = f'<div class="yc-progreso" aria-label="Paso {n} de 7"><div class="yc-barras">{barras}</div><span class="yc-etiqueta">{etiqueta}</span></div>'
    else:
        progreso = f'<div class="yc-progreso"><span class="yc-etiqueta">{"Dudas frecuentes" if slug == "0-dudas" else "Contacto"}</span></div>'
    titulo, sub = TITULOS[slug]
    sub_html = f'<p class="yc-sub">{sub}</p>' if sub else ""
    return f'<header class="yc-titular">{progreso}<h1>{titulo}</h1>{sub_html}</header>'

def documento(slug, cuerpo, portada=False):
    titulo, desc, _ = PAGINAS[slug]
    canon = "https://www.yomeconfieso.es/" + ("" if slug == "inicio" else slug + "/")
    cabeza = f"""<!DOCTYPE html>
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
<meta name="theme-color" content="#2A2238">
<link rel="icon" href="/favicon.png">
<link rel="apple-touch-icon" href="/img/icono-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/estilo.css">
</head>
"""
    if portada:
        return cabeza + f"""<body class="yc yc-inicio">
{cuerpo}
</body>
</html>
"""
    return cabeza + f"""<body class="yc">
<aside class="yc-cuadro">
  <a class="yc-marca" href="/" aria-label="Inicio"><img src="/img/logo.png" alt="Yo me confieso"></a>
  <nav class="yc-camino" aria-label="Tu camino"><p>Tu camino</p>{camino_html(slug)}</nav>
</aside>
<div class="yc-cuerpo">
  <header class="yc-barra">
    <details class="yc-menu-movil">
      <summary aria-label="Abrir menú"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>
      <nav aria-label="Menú">{menu_html(slug)}<hr>{camino_html(slug)}</nav>
    </details>
    <nav class="yc-menu" aria-label="Menú">{menu_html(slug)}</nav>
  </header>
  <main class="yc-principal">
{cabecera_pagina(slug)}
{cuerpo}
  </main>
  <footer class="yc-pie">Esta web te ayuda a prepararte. El perdón lo da el sacerdote en la confesión. · <a href="/0-dudas/">Dudas</a> · <a href="/contacto/">Contacto</a></footer>
</div>
</body>
</html>
"""

PORTADA = """<div class="yc-portada">
  <div class="yc-portada-cuadro">
    <nav class="yc-menu yc-menu-claro" aria-label="Menú"><a href="/0-intro/">Qué es la confesión</a><a href="/0-dudas/">Dudas</a><a href="/contacto/">Contacto</a></nav>
    <h1><img src="/img/logo.png" alt="Yo me confieso"></h1>
    <p class="yc-cita">«Es un encuentro vivo de amor y sanación que manifiesta de manera palpable la ternura infinita del Corazón de Jesús.»</p>
  </div>
  <main class="yc-portada-texto">
    <nav class="yc-menu yc-menu-portada" aria-label="Menú"><a href="/0-intro/">Qué es la confesión</a><a href="/0-dudas/">Dudas</a><a href="/contacto/">Contacto</a></nav>
    <p class="yc-antetitulo">Examen de conciencia y confesión</p>
    <p class="yc-lema">Tu guía paso a paso para el examen de conciencia y la confesión</p>
    <p class="yc-entradilla">Sin prisas, a tu ritmo. Un examen sencillo, unas preguntas para ti y el diálogo con el sacerdote en la palma de la mano.</p>
    <p class="yc-antetitulo yc-elige">Elige tu examen</p>
    <div class="yc-examenes">
      <a class="yc-examen principal" href="/2-examen/"><span><strong>Adultos</strong><small>Más de 30 años</small></span>FLECHA</a>
      <a class="yc-examen" href="/2-examen-jovenes/"><span><strong>Jóvenes</strong><small>De 15 a 30 años</small></span>FLECHA</a>
      <a class="yc-examen" href="/2-examen-primaria/"><span><strong>Chicos y chicas</strong><small>De 10 a 15 años</small></span>FLECHA</a>
    </div>
    <a class="yc-enlace" href="/0-intro/">¿Qué es la confesión? Empieza por aquí</a>
    <p class="yc-nota">Esta web te ayuda a prepararte. El perdón lo da el sacerdote en la confesión.</p>
  </main>
</div>""".replace("FLECHA", ICONO_FLECHA)

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
        codigo = ""  # la portada nueva no usa los fragmentos antiguos
        partes.append(PORTADA)
    for t in textos_antes:
        clase = "yc-texto yc-aviso" if "NO SUSTITUYE" in t else "yc-texto"
        partes.append(f'<div class="{clase}">{urls(t)}</div>')
    if codigo:
        partes.append(f'<div class="pagina{" ancha" if ancha else ""}">\n{codigo}\n</div>')
    for t in textos_despues:
        partes.append(f'<div class="yc-texto">{urls(t)}</div>')
    if slug == "5-ayudas":
        partes.append('<a class="yc-boton" href="/6-paso-a-paso/">Estoy preparado ' + ICONO_FLECHA + '</a>')
    if slug == "0-dudas":
        partes.append('<a class="yc-boton secundario" href="/">Volver al inicio</a>')
    html = documento(slug, "\n".join(partes), portada=(slug == "inicio"))
    if slug.startswith("2-examen"):
        for viejo, nuevo in [("#c0392b", "#9E3B52"), ("#e67e22", "#C7843A"), ("#27ae60", "#5E8F6E"),
                             ("ctx.fillStyle   = '#ecf0f1'", "ctx.fillStyle   = '#ECE8F3'"),
                             ("ctx.fillStyle    = '#2c3e50'", "ctx.fillStyle    = '#2A2238'")]:
            html = html.replace(viejo, nuevo)
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
