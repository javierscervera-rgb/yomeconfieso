#!/usr/bin/env python3
"""Migración única: convierte los fragmentos de IONOS (carpeta original/)
en páginas completas con cabecera, menú y pie comunes.
Después de ejecutarlo, las páginas generadas son la fuente que se edita."""
import re, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import hashlib
VERSION_CSS = hashlib.md5(open(os.path.join(RAIZ, "css", "estilo.css"), "rb").read()).hexdigest()[:8]
VERSION_COMUN = hashlib.md5(open(os.path.join(RAIZ, "js", "comun.js"), "rb").read()).hexdigest()[:8]
ORIG = os.path.join(RAIZ, "original")

PAGINAS = {
    # slug: (título <title>, descripción, ancha)
    "inicio": ("yomeconfieso · Tu guía para confesarte", "Tu guía paso a paso para el examen de conciencia y la confesión.", False),
    "saber-mas": ("Saber más sobre la confesión · yomeconfieso", "Qué es el sacramento de la Confesión, sus cinco partes, vídeos y dudas frecuentes.", False),
    "2-examen": ("Examen de conciencia para adultos · yomeconfieso", "Examen de conciencia interactivo para adultos.", True),
    "2-examen-jovenes": ("Examen de conciencia para jóvenes · yomeconfieso", "Examen de conciencia interactivo para jóvenes de 15 a 30 años.", True),
    "2-examen-primaria": ("Examen de conciencia para chicos/as · yomeconfieso", "Examen de conciencia interactivo para chicos y chicas de 10 a 15 años.", True),
    "3-preguntas": ("Preguntas del examen · yomeconfieso", "Preguntas del examen de conciencia.", False),
    "3-preguntas-jovenes": ("Preguntas del examen · yomeconfieso", "Preguntas del examen de conciencia para jóvenes.", False),
    "3-preguntas-primaria": ("Preguntas del examen · yomeconfieso", "Preguntas del examen de conciencia para chicos y chicas.", False),
    "comenzar": ("Comenzamos: examen de conciencia · yomeconfieso", "Primera parte de la confesión: el examen de conciencia. Elige tu examen.", False),
    "dolor": ("Dolor de los pecados · yomeconfieso", "Segunda parte de la confesión: el dolor de los pecados.", False),
    "proposito": ("Propósito de la enmienda · yomeconfieso", "Tercera parte de la confesión: el propósito de la enmienda.", False),
    "5-ayudas": ("Ayudas antes de confesarte · yomeconfieso", "Oraciones, vídeo y parroquias cercanas.", False),
    "6-paso-a-paso": ("La confesión paso a paso · yomeconfieso", "Guía para el momento de la confesión.", False),
    "7-final": ("Terminando · yomeconfieso", "Después de la confesión.", False),
    "contacto": ("Contacto · yomeconfieso", "Escríbenos.", False),
}

# páginas antiguas que ahora redirigen
REDIRECCIONES = {"0-intro": "/saber-mas/#que-es", "0-dudas": "/saber-mas/#dudas",
                 "1-prepara": "/saber-mas/#videos", "4-dos-cosas": "/dolor/", "5-ayudas": "/6-paso-a-paso/"}

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

PARTES = [  # (número, nombre, [(slug base, subpaso)])
    (1, "Examen de conciencia", [("comenzar", "Elige tu examen"), ("2-examen", "Examen"), ("3-preguntas", "Preguntas")]),
    (2, "Dolor de los pecados", [("dolor", None)]),
    (3, "Propósito de la enmienda", [("proposito", None)]),
    (4, "Decir los pecados al confesor", [("6-paso-a-paso", None)]),
    (5, "Cumplir la penitencia", [("7-final", None)]),
]

TITULOS = {  # título, subtítulo
    "saber-mas": ("Saber más", "Qué es la confesión, sus cinco partes, vídeos y dudas"),
    "comenzar": ("Examen de conciencia", ""),
    "2-examen": ("Examen de conciencia", "Para adultos"),
    "2-examen-jovenes": ("Examen de conciencia", "Para jóvenes"),
    "2-examen-primaria": ("Examen de conciencia", "Para chicos y chicas"),
    "3-preguntas": ("Algunas preguntas preparadas para ti", ""),
    "3-preguntas-jovenes": ("Algunas preguntas para jóvenes como tú", ""),
    "3-preguntas-primaria": ("Algunas preguntas para chicos y chicas como tú", ""),
    "dolor": ("Dolor de los pecados", ""),
    "proposito": ("Propósito de la enmienda", ""),
    "5-ayudas": ("Algunas ayudas antes de confesarte", ""),
    "6-paso-a-paso": ("La confesión paso a paso", ""),
    "7-final": ("Cumplir la penitencia", "Terminando…"),
    "contacto": ("¿Quieres decirme algo?", ""),
}

VIDEOS = {  # explicaciones breves (lista «YOMECONFIESO: La confesión paso a paso»)
    "examen": ("El examen de conciencia", "iy600PwVhNU"),
    "dolor": ("El dolor de los pecados", "QtboE1KXdEU"),
    "proposito": ("El propósito de la enmienda", "_gNeeQXcg-Q"),
    "decir": ("Decir los pecados al confesor", "kIClPrOVQeI"),
    "penitencia": ("Cumplir la penitencia", "0_k8zUC86ck"),
}
VIDEO_DE = {"2-examen": "examen", "2-examen-jovenes": "examen", "2-examen-primaria": "examen",
            "dolor": "dolor", "proposito": "proposito", "6-paso-a-paso": "decir", "7-final": "penitencia"}

def video_html(clave):
    titulo, yt = VIDEOS[clave]
    return (f'<details class="yc-video"><summary><span class="yc-video-icono" aria-hidden="true">▶</span>'
            f'<span><small>Para profundizar</small>Explicación: «{titulo}»</span></summary>'
            f'<div class="yc-video-marco"><iframe data-src="https://www.youtube.com/embed/{yt}" title="{titulo}" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div></details>')

ICONO_FLECHA = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

def variante(slug):
    for v in ("-jovenes", "-primaria"):
        if slug.endswith(v):
            return v
    return ""

def parte_de(slug):
    for n, nombre, subs in PARTES:
        for i, (base, sub) in enumerate(subs):
            if slug == base or slug.startswith(base + "-"):
                return n, nombre, i, sub
    return None, None, None, None

def href_base(base, slug):
    v = variante(slug)
    if base in ("2-examen", "3-preguntas") and v:
        return f"/{base}{v}/"
    return f"/{base}/"

def camino_html(slug):
    actual, _, sub_actual, _ = parte_de(slug)
    saber = ' class="yc-saber activo" aria-current="page"' if slug == "saber-mas" else ' class="yc-saber"'
    items = [f'<a href="/saber-mas/"{saber}><span>i</span>Saber más</a><ol class="yc-partes-lista">']
    for n, nombre, subs in PARTES:
        estado = "activo" if n == actual else ("hecho" if actual and n < actual else "")
        cur = ' aria-current="step"' if n == actual else ""
        items.append(f'<li class="{estado}"><a href="{href_base(subs[0][0], slug)}" data-parte="{n}"{cur}><span>{n}</span>{nombre}</a>')
        if n == actual and len(subs) > 1:
            items.append('<ul>')
            for i, (base, sub) in enumerate(subs):
                c = ' class="activo"' if i == sub_actual else ""
                items.append(f'<li{c}><a href="{href_base(base, slug)}">{sub}</a></li>')
            items.append('</ul>')
        items.append('</li>')
    items.append('</ol>')
    return "".join(items)

MENU_ENLACES = [("Inicio", "/"), ("Saber más", "/saber-mas/"), ("Dudas", "/saber-mas/#dudas"), ("Contacto", "/contacto/")]

def menu_html(slug):
    activo = {"inicio": "/", "saber-mas": "/saber-mas/", "contacto": "/contacto/"}.get(slug)
    return "".join(
        f'<a href="{h}"' + (' aria-current="page"' if h == activo else '') + f'>{n}</a>'
        for n, h in MENU_ENLACES)

def menu_desplegable(slug, clase=""):
    return (f'<details class="yc-menu-movil {clase}">'
            '<summary aria-label="Abrir menú"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>'
            f'<nav aria-label="Menú">{menu_html(slug)}<hr>{camino_html(slug)}</nav></details>')

def cabecera_pagina(slug):
    n, nombre, i, sub = parte_de(slug)
    if n is not None:
        pasos = []
        for m, nom, _ in PARTES:
            clase = "activo" if m == n else ("hecho" if m < n else "")
            pasos.append(f'<li class="{clase}"><span class="yc-num">{m}</span><span class="yc-nom">{nom}</span></li>')
        detalle = f" · {sub}" if sub else ""
        progreso = (f'<nav class="yc-pasos" aria-label="Las cinco partes de la confesión"><ol>{"".join(pasos)}</ol></nav>'
                    f'<p class="yc-etiqueta">Parte {n} de 5 · {nombre}{detalle}</p>')
    else:
        etiqueta = {"saber-mas": "Antes de empezar", "contacto": "Contacto"}.get(slug, "")
        progreso = f'<p class="yc-etiqueta">{etiqueta}</p>'
    titulo, sub_t = TITULOS[slug]
    sub_html = f'<p class="yc-sub">{sub_t}</p>' if sub_t else ""
    return f'<header class="yc-titular">{progreso}<h1>{titulo}</h1>{sub_html}</header>'

def documento(slug, cuerpo, portada=False):
    titulo, desc, _ = PAGINAS[slug]
    canon = "https://www.yomeconfieso.es/" + ("" if slug == "inicio" else slug + "/")
    cabeza = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<title>{titulo}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://www.yomeconfieso.es/img/abrazo.jpg">
<meta property="og:locale" content="es_ES">
<meta name="theme-color" content="#2A2238">
<script>if (location.protocol === "http:" && /yomeconfieso[.]es$/.test(location.hostname)) location.replace("https:" + location.href.slice(5));</script>
<link rel="icon" href="/favicon.png">
<link rel="apple-touch-icon" href="/img/icono-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/estilo.css?v={VERSION_CSS}">
</head>
"""
    if portada:
        return cabeza + f"""<body class="yc yc-inicio">
{cuerpo}
<script src="/js/comun.js?v={VERSION_COMUN}"></script>
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
  <footer class="yc-pie">Esta web te ayuda a prepararte. El perdón lo da el sacerdote en la confesión. · <a href="/saber-mas/#dudas">Dudas</a> · <a href="/contacto/">Contacto</a></footer>
</div>
<script src="/js/comun.js?v={VERSION_COMUN}"></script>
</body>
</html>
"""

PORTADA = """<div class="yc-portada">
  <div class="yc-portada-cuadro">
MENU_PORTADA
    <h1><img src="/img/logo.png" alt="Yo me confieso"></h1>
    <p class="yc-cita">«Es un encuentro vivo de amor y sanación que manifiesta de manera palpable la ternura infinita del Corazón de Jesús.»</p>
  </div>
  <main class="yc-portada-texto">
    <p class="yc-antetitulo">Examen de conciencia y confesión</p>
    <p class="yc-lema">Tu guía paso a paso para el examen de conciencia y la confesión</p>
    <p class="yc-entradilla">Sin prisas, a tu ritmo. Un examen sencillo, unas preguntas para ti y el diálogo con el sacerdote en la palma de la mano.</p>
    <div class="yc-portada-botones">
      <a class="yc-boton-par" href="/comenzar/">Comenzamos</a>
      <a class="yc-boton-par" href="/saber-mas/">Saber más</a>
    </div>
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
        partes.append(PORTADA.replace("MENU_PORTADA", menu_desplegable("inicio", "yc-menu-portada-btn")))
    for t in textos_antes:
        clase = "yc-texto yc-aviso" if "NO SUSTITUYE" in t else "yc-texto"
        partes.append(f'<div class="{clase}">{urls(t)}</div>')
    if codigo:
        partes.append(f'<div class="pagina{" ancha" if ancha else ""}">\n{codigo}\n</div>')
    for t in textos_despues:
        partes.append(f'<div class="yc-texto">{urls(t)}</div>')
    if slug == "7-final":
        partes.append(MI_PROPOSITO)
    if slug in VIDEO_DE:
        partes.append(video_html(VIDEO_DE[slug]))
    if slug == "5-ayudas":
        partes.append('<a class="yc-boton" href="/6-paso-a-paso/">Estoy preparado ' + ICONO_FLECHA + '</a>')
    escribir(slug, documento(slug, "\n".join(partes), portada=(slug == "inicio")))

def escribir(slug, html):
    if slug.startswith("2-examen"):
        for viejo, nuevo in [("#c0392b", "#9E3B52"), ("#e67e22", "#C7843A"), ("#27ae60", "#5E8F6E"),
                             ("ctx.fillStyle   = '#ecf0f1'", "ctx.fillStyle   = '#ECE8F3'"),
                             ("ctx.fillStyle    = '#2c3e50'", "ctx.fillStyle    = '#2A2238'")]:
            html = html.replace(viejo, nuevo)
    # vídeos nuevos (mejor editados) en lugar de las homilías completas
    for viejo, nuevo in [("dOVuHuXlZhY", "kQnzisJ5YFg"), ("8kwMIOBhx_Q", "iy600PwVhNU"), ("HL07-Zv__eM", "QtboE1KXdEU"),
                         ("MfxZ74nGVFA", "_gNeeQXcg-Q"), ("6f6s4foZRpU", "kIClPrOVQeI"), ("qKgrMTU_SRI", "0_k8zUC86ck")]:
        html = html.replace(viejo, nuevo)
    html = html.replace("Si quieres saber más aquí te dejo 6 vídeos sobre los aspectos esenciales de la Confesión. Son homilías pronunciadas en el contexto de una Novena a la Virgen del Pilar.",
                        "Si quieres saber más, aquí tienes seis vídeos breves que explican los aspectos esenciales de la Confesión.")
    html = html.replace("/4-dos-cosas/", "/dolor/").replace("/4-dos-cosas", "/dolor/")
    for mal, bien in [("te confesaros", "te confesaste"), ("cercansa", "cercanas"), ("pero pero", "pero"), ("momento en vayas", "momento en que vayas")]:
        html = html.replace(mal, bien)
    # rutas relativas: funcionan igual en el dominio propio y en la vista previa de github.io
    pre = "./" if slug == "inicio" else "../"
    html = re.sub(r'((?:href|src|data-url)=|location\.href\s*=\s*)(["\'])/(?!/)', lambda m: m.group(1) + m.group(2) + pre, html)
    ruta = os.path.join(RAIZ, "index.html" if slug == "inicio" else os.path.join(slug, "index.html"))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    open(ruta, "w", encoding="utf-8").write(html)
    print("ok", slug, len(html))

# ---------- páginas nuevas ----------
MI_PROPOSITO = """<div class="yc-texto yc-mi-proposito" id="mi-proposito-caja" hidden>
  <div class="yc-tarjeta"><p class="yc-tarjeta-titulo">Tu propósito</p><p id="mi-proposito"></p></div>
</div>"""

def parrafos_story(slug):
    txt = open(os.path.join(ORIG, slug + ".html"), encoding="utf-8").read()
    story = re.search(r'<div class="story">(.*?)</div>', txt, re.S).group(1)
    return [re.sub(r"\s+", " ", re.sub(r"&nbsp;", " ", p)).strip() for p in re.findall(r"<p[^>]*>(.*?)</p>", story, re.S)]

def codigo_de(slug):
    for tipo, contenido in trocear(slug):
        if tipo == "CODE":
            return urls(arreglos(slug, limpiar_codigo(contenido)))
    return ""

def SIN_EXAMENES(codigo):
    codigo, n = re.subn(r"\s*<!-- BOTONES DE EXAMEN -->.*?(?=<script>)", "\n", codigo, count=1, flags=re.S)
    assert n == 1, "no se encontró la elección de examen en Prepara"
    return codigo

def construir_saber_mas():
    intro = parrafos_story("0-intro")
    intro_html = "".join(f"<p>{p}</p>" for p in intro if "Recibid el Espíritu Santo" not in p)
    cita = next(p for p in intro if "Recibid el Espíritu Santo" in p)
    m = re.search(r'"(Recibid.*?)"\s*\((Jn [^)]*)\)', cita)
    cita_html = f'<p>{cita.split(":")[0]}:</p><blockquote class="yc-cita-biblica">«{m.group(1)}»<cite>{m.group(2)}</cite></blockquote>' if m else f"<p>{cita}</p>"
    partes_html = "".join(
        f'<li><span class="yc-num">{n}</span><div><strong>{nombre}</strong><p>{desc}</p></div></li>'
        for n, nombre, desc in [
            (1, "Examen de conciencia", "Mirar con calma tu vida a la luz de Dios y reconocer tus pecados."),
            (2, "Dolor de los pecados", "Arrepentirte de corazón por haber ofendido a Dios."),
            (3, "Propósito de la enmienda", "Decidir poner los medios para no volver a caer."),
            (4, "Decir los pecados al confesor", "Confesarlos con sencillez al sacerdote y recibir la absolución."),
            (5, "Cumplir la penitencia", "Rezar o hacer lo que el sacerdote te indique."),
        ])
    cuerpo = f"""<nav class="yc-indice" aria-label="En esta página">
  <a href="#que-es">¿Qué es?</a><a href="#partes">Las cinco partes</a><a href="#dudas">Dudas</a><a href="#videos">Vídeos</a>
</nav>
<section class="yc-seccion" id="que-es">
  <div class="yc-texto"><h2>El sacramento de la misericordia</h2>{intro_html.split("</p>", 1)[0]}</p>{cita_html}{intro_html.split("</p>", 1)[1]}</div>
</section>
<section class="yc-seccion" id="partes">
  <div class="yc-texto"><h2>Las cinco partes de la confesión</h2>
  <p>La web te acompaña en cada una de ellas, en este orden:</p>
  <ol class="yc-lista-partes">{partes_html}</ol></div>
</section>
<section class="yc-seccion" id="dudas">
  <div class="yc-texto"><h2>Dudas frecuentes</h2><p>Las preguntas que más nos llegan por correo, agrupadas por temas.</p></div>
  <div class="pagina">
{codigo_de("0-dudas")}
  </div>
</section>
<section class="yc-seccion" id="videos">
  <div class="yc-texto"><h2>Vídeos</h2></div>
  <div class="pagina">
{SIN_EXAMENES(codigo_de("1-prepara"))}
  </div>
</section>
<a class="yc-boton" href="/comenzar/">Comenzamos {ICONO_FLECHA}</a>"""
    escribir("saber-mas", documento("saber-mas", cuerpo))

def construir_dolor_y_proposito():
    p = parrafos_story("4-dos-cosas")
    contricion = """<div class="yc-texto"><div class="yc-tarjeta yc-oracion">
  <p class="yc-tarjeta-titulo">Acto de contrición</p>
  <p>Señor mío Jesucristo, Dios y Hombre verdadero, Creador y Redentor mío; por ser Vos quien sois, Bondad infinita, y porque os amo sobre todas las cosas, me pesa de todo corazón haberos ofendido; también me pesa porque puedo condenarme con las penas del infierno. Ayudado de vuestra divina gracia, propongo firmemente nunca más pecar, confesarme y cumplir la penitencia que me fuera impuesta. Amén.</p>
</div></div>"""
    dolor = (f'<div class="yc-texto yc-lectura">' + "".join(f"<p>{x}</p>" for x in p[:3]) +
             f'<p class="yc-pausa">{p[3]}</p></div>' + contricion + video_html("dolor") +
             f'<a class="yc-boton" href="/proposito/">Continuar {ICONO_FLECHA}</a>')
    escribir("dolor", documento("dolor", dolor))
    proposito = ('<div class="yc-texto yc-lectura">'
                 '<p>Ahora que estás arrepentido pregúntate qué vas a hacer para que no vuelva a pasar, qué momentos, circunstancias, personas, rutinas debes evitar para que no suceda. Dios nos perdona siempre pero nos pide que, cada vez, tengamos un propósito firme y concreto de no volver a hacer ese pecado.</p>'
                 '<p class="yc-pausa">Quizá tendrías que hacer algo concreto para evitarlo…</p></div>'
                 '<div class="yc-texto"><div class="yc-tarjeta">'
                 '<label class="yc-tarjeta-titulo" for="proposito">Si quieres escribe aquí alguna cosa que vas a cambiar.</label>'
                 '<textarea id="proposito" rows="3"></textarea>'
                 '<p class="yc-mini">Se guarda solo en este dispositivo y lo verás al terminar.</p></div></div>' +
                 video_html("proposito") +
                 f'<a class="yc-boton" href="/6-paso-a-paso/">Continuar {ICONO_FLECHA}</a>')
    escribir("proposito", documento("proposito", proposito))

def construir_comenzar():
    examenes = "".join(
        f'<a class="yc-examen" href="/{slug}/"><span><strong>{t}</strong><small>{sub}</small></span>{ICONO_FLECHA}</a>'
        for slug, t, sub in [("2-examen", "Adultos", "Más de 30 años"),
                             ("2-examen-jovenes", "Jóvenes", "De 15 a 30 años"),
                             ("2-examen-primaria", "Chicos y chicas", "De 10 a 15 años")])
    cuerpo = f"""<div class="yc-texto yc-lectura">
  <p>Empezamos por la primera de las cinco partes de la confesión: el <strong>examen de conciencia</strong>.</p>
  <p>Examinar la conciencia es mirar con calma tu vida a la luz del amor de Dios para reconocer en qué le has fallado a Él, a los demás y a ti mismo desde tu última confesión. No se trata de agobiarte, sino de ver con sinceridad lo que hay en tu corazón para poder ponerlo en manos de Dios.</p>
  <p>Te ayudaremos en dos momentos: primero, un juego sencillo para ordenar unas palabras; después, unas preguntas preparadas según lo que hayas elegido.</p>
</div>
<div class="yc-texto"><p class="yc-antetitulo yc-izq">Elige tu examen</p><div class="yc-examenes yc-examenes-lista">{examenes}</div></div>"""
    escribir("comenzar", documento("comenzar", cuerpo))

def construir_redirecciones():
    for viejo, nuevo in REDIRECCIONES.items():
        destino = ".." + nuevo
        html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>yomeconfieso</title>
<link rel="canonical" href="https://www.yomeconfieso.es{nuevo.split('#')[0]}">
<meta http-equiv="refresh" content="0; url={destino}">
<meta name="robots" content="noindex">
<script>location.replace("{destino}");</script></head>
<body><p><a href="{destino}">Esta página se ha movido. Pulsa aquí.</a></p></body></html>
"""
        ruta = os.path.join(RAIZ, viejo, "index.html")
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        open(ruta, "w", encoding="utf-8").write(html)
        print("redirección", viejo, "->", nuevo)

NORMALES = ["inicio", "2-examen", "2-examen-jovenes", "2-examen-primaria", "3-preguntas", "3-preguntas-jovenes",
            "3-preguntas-primaria", "6-paso-a-paso", "7-final", "contacto"]

if __name__ == "__main__":
    for s in NORMALES:
        construir(s)
    construir_saber_mas()
    construir_comenzar()
    construir_dolor_y_proposito()
    construir_redirecciones()
