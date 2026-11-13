#!/usr/bin/env python3
"""Paso a paso: botón «Buscar iglesias cercanas» desplegable, botón «Comenzar» y el diálogo en ventana.
Cumplir la penitencia: botón al formulario de contacto."""
import os, re, hashlib
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = hashlib.md5(open(os.path.join(RAIZ, "js", "parroquias.js"), "rb").read()).hexdigest()[:8]

def cambiar(s, viejo, nuevo):
    assert viejo in s, viejo[:80]
    return s.replace(viejo, nuevo, 1)

# ---------- 6 · Paso a paso ----------
ruta = os.path.join(RAIZ, "6-paso-a-paso", "index.html")
s = open(ruta, encoding="utf-8").read()
if 'id="dialogoModal"' not in s:
    s = cambiar(s, 'Si no sabes dónde puedes confesarte puedes buscar las iglesias cercanas pulsando <a href="../5-ayudas/">AQUÍ</a> y luego regresar.',
                'Si no sabes dónde puedes confesarte, aquí abajo puedes buscar las iglesias cercanas.')
    s = cambiar(s, '<div class="pagina">',
        '<div class="yc-texto yc-acciones">'
        '<details class="yc-desplegable" id="buscarIglesias"><summary>'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>'
        'Buscar iglesias cercanas</summary><div id="parroquias" class="parroquias"></div></details>'
        '<button type="button" class="yc-boton yc-boton-izq" id="empezarDialogo">Comenzar</button></div>\n'
        '<div id="dialogoModal" class="juego-modal" hidden role="dialog" aria-modal="true" aria-label="La confesión paso a paso">'
        '<div class="juego-modal-cabecera"><span>La confesión paso a paso</span>'
        '<button type="button" id="cerrarDialogo" class="juego-cerrar" aria-label="Cerrar">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>'
        '<div class="juego-modal-cuerpo"><div class="pagina">')
    s = cambiar(s, "    </script>\n</div>\n<details class=\"yc-video\">", "    </script>\n</div></div></div>\n<details class=\"yc-video\">")
    s = cambiar(s, """        window.onload = () => {
            setTimeout(() => {
                avanzarDialogo();
            }, 400);
        };""", """        window.iniciarDialogo = () => {
            setTimeout(() => {
                avanzarDialogo();
            }, 400);
        };""")
    s = cambiar(s, "</body>", f"""<script>
(function () {{
  var modal = document.getElementById("dialogoModal");
  var empezar = document.getElementById("empezarDialogo");
  var empezado = false;
  empezar.addEventListener("click", function () {{
    modal.hidden = false;
    document.body.classList.add("juego-abierto");
    if (!empezado) {{ empezado = true; window.iniciarDialogo(); empezar.textContent = "Continuar"; }}
  }});
  document.getElementById("cerrarDialogo").addEventListener("click", function () {{
    modal.hidden = true;
    document.body.classList.remove("juego-abierto");
  }});
  var iglesias = document.getElementById("buscarIglesias");
  var buscadas = false;
  iglesias.addEventListener("toggle", function () {{
    if (iglesias.open && !buscadas && window.listarParroquias) {{ buscadas = true; window.listarParroquias(); }}
  }});
}})();
</script>
<script src="../js/parroquias.js?v={V}"></script>
</body>""")
    open(ruta, "w", encoding="utf-8").write(s)
    print("ok 6-paso-a-paso")

# ---------- 7 · Cumplir la penitencia ----------
ruta = os.path.join(RAIZ, "7-final", "index.html")
s = open(ruta, encoding="utf-8").read()
if "contacto-boton" not in s:
    s, n = re.subn(r'<p class="contacto-final">.*?</p>',
                   '<p class="contacto-final">¿Quieres decirme algo?</p>\n'
                   '<div class="contacto-boton"><a class="yc-boton" href="../contacto/">Formulario de contacto</a></div>', s, count=1, flags=re.S)
    assert n == 1
    open(ruta, "w", encoding="utf-8").write(s)
    print("ok 7-final")
