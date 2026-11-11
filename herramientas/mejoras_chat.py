#!/usr/bin/env python3
"""Preguntas: la pregunta activa siempre en el centro de la pantalla.
Paso a paso: el último mensaje se centra en pantalla. Final: texto centrado."""
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cambiar(s, viejo, nuevo, n=1):
    assert viejo in s, viejo[:80]
    return s.replace(viejo, nuevo, n)

def preguntas(ruta):
    s = open(ruta, encoding="utf-8").read()
    if "function centrar(" in s:
        return print("ya aplicado", ruta)
    s = cambiar(s, """    height: 75vh;
    overflow-x: hidden;
    overflow-y: auto;
    display: flex;""", """    padding-bottom: 45vh; /* espacio para poder centrar la última pregunta */
    display: flex;""")
    s = cambiar(s, """.pagina #progress-container {
    width: 95%;""", """.pagina #progress-container {
    position: sticky;
    bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,.15);
    width: 95%;""")
    s = cambiar(s, "let preguntas = [];", """function centrar(el) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
}

let preguntas = [];""")
    # nueva pregunta -> al centro
    s = cambiar(s, "    chat.scrollTop = chat.scrollHeight;", "    centrar(msg);")
    # final -> quitar el hueco y mostrar el cierre desde arriba
    s = cambiar(s, "    chat.scrollTop = chat.scrollHeight;", """    chat.style.paddingBottom = "20px";
    document.getElementById("progress-container").style.display = "none";
    msg.scrollIntoView({ behavior: "smooth", block: "start" });""")
    assert "chat.scrollTop" not in s
    open(ruta, "w", encoding="utf-8").write(s)
    print("ok", ruta)

def paso_a_paso(ruta):
    s = open(ruta, encoding="utf-8").read()
    if "function centrarUltimo(" in s:
        return print("ya aplicado", ruta)
    s = cambiar(s, ".pagina .chat-body { min-height: 60vh; }", ".pagina .chat-body { min-height: 60vh; padding-bottom: 40vh; }")
    s = cambiar(s, "        function agregarAclaracion(texto) {", """        // Mantiene el último mensaje en el centro de la pantalla
        function centrarUltimo() {
            const el = chatBody.lastElementChild;
            if (!el) return;
            const r = el.getBoundingClientRect();
            if (r.top + r.height / 2 > window.innerHeight / 2) {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
        function agregarAclaracion(texto) {""")
    s = s.replace("chatBody.scrollTop = chatBody.scrollHeight;", "centrarUltimo();")
    # al terminar, quitar el hueco inferior
    s = cambiar(s, "            chatBody.appendChild(terminarBtn);", "            chatBody.appendChild(terminarBtn);\n            chatBody.style.paddingBottom = '30px';")
    open(ruta, "w", encoding="utf-8").write(s)
    print("ok", ruta)

def final(ruta):
    s = open(ruta, encoding="utf-8").read()
    s = s.replace(""".pagina .story p:first-child {
  margin-top:8px;
  text-align:left;
  padding:0 20px;
}""", """.pagina .story p:first-child {
  margin-top:8px;
}""")
    open(ruta, "w", encoding="utf-8").write(s)
    print("ok", ruta)

for slug in ("3-preguntas", "3-preguntas-jovenes", "3-preguntas-primaria"):
    preguntas(os.path.join(RAIZ, slug, "index.html"))
paso_a_paso(os.path.join(RAIZ, "6-paso-a-paso", "index.html"))
final(os.path.join(RAIZ, "7-final", "index.html"))
