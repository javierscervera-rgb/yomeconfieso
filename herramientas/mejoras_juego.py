#!/usr/bin/env python3
"""Mejoras del juego del examen (adultos, jóvenes, chicos/as):
pastillas que recorren todo el ancho, aceleración solo de la palabra tocada,
botones + / − de velocidad, ancho de escritorio y flechas del teclado."""
import os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cambiar(s, viejo, nuevo, n=1):
    assert s.count(viejo) >= 1, viejo[:80]
    return s.replace(viejo, nuevo, n)

CSS = """
.pagina .scroll-container { max-width: 100%; cursor: grab; }
.pagina .scroll-container.arrastrando { cursor: grabbing; }
.pagina .scroll-container::-webkit-scrollbar { display: none; }
.pagina .scroll-container { scrollbar-width: none; }
.pagina .graph-wrapper { width: auto; min-width: 0; }
.pagina #mainSvg { width: 900px; }
.pagina .juego { position: relative; width: 100%; max-width: 760px; margin: 0 auto; }
.pagina .velocidad {
    position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
    z-index: 30; display: flex; flex-direction: column; align-items: center; gap: 8px;
}
.pagina .velocidad button {
    width: 46px; height: 46px; border-radius: 50%; border: none; cursor: pointer;
    background: rgb(89,193,192); color: #fff; font: 700 1.6rem/1 Arial, sans-serif;
    box-shadow: 0 4px 10px rgba(0,0,0,.2); touch-action: manipulation;
}
.pagina .velocidad button:disabled { opacity: .35; cursor: default; }
.pagina .velocidad span {
    font: 700 .85rem Arial, sans-serif; color: #2c3e50; background: rgba(255,255,255,.9);
    border-radius: 8px; padding: 2px 6px;
}
.pagina .ayuda-teclado { display: none; text-align: center; font-size: .9rem; color: #555; margin: 8px 0 0; }
@media (hover: hover) and (pointer: fine) { .pagina .ayuda-teclado { display: block; } }
</style>"""

def mejorar(ruta):
    s = open(ruta, encoding="utf-8").read()
    if "class=\"velocidad\"" in s:
        print("ya aplicado", ruta); return
    # --- CSS ---
    s = re.sub(r"\.pagina \.scroll-container \{ max-width: 440px; cursor: grab; \}\n\.pagina \.scroll-container\.arrastrando \{ cursor: grabbing; \}\n</style>", CSS, s)
    assert ".pagina .velocidad" in s
    # --- HTML: envoltorio con los botones de velocidad ---
    s = cambiar(s, '<div class="scroll-container" id="scrollContainer">',
                '<div class="juego">\n            <div class="scroll-container" id="scrollContainer">')
    s = cambiar(s, """                    <div id="stackedWords"></div>
                </div>
            </div>
        </div>""", """                    <div id="stackedWords"></div>
                </div>
            </div>
            <div class="velocidad" aria-label="Velocidad de caída">
                <button type="button" id="velMas" aria-label="Más rápido">+</button>
                <span id="velTexto">x1</span>
                <button type="button" id="velMenos" aria-label="Más despacio">−</button>
            </div>
            <p class="ayuda-teclado">Usa las flechas ← → del teclado para mover las cajas y ↓ para que la palabra caiga más rápido.</p>
            </div>
        </div>""")
    # --- velocidad: base ajustable + aceleración solo de la palabra tocada ---
    s = cambiar(s, """            let fallSpeed  = FALL_SPEED_NORMAL;
            let boosted    = false;""", """            const VELOCIDADES = [0.5, 0.75, 1, 1.5, 2, 3];
            let nivelVel   = VELOCIDADES.indexOf(FALL_SPEED_NORMAL);
            let fallSpeed  = VELOCIDADES[nivelVel];
            const velMas   = document.getElementById('velMas');
            const velMenos = document.getElementById('velMenos');
            const velTexto = document.getElementById('velTexto');
            function pintarVelocidad() {
                fallSpeed = VELOCIDADES[nivelVel];
                velTexto.textContent = 'x' + String(fallSpeed).replace('.', ',');
                velMas.disabled   = nivelVel === VELOCIDADES.length - 1;
                velMenos.disabled = nivelVel === 0;
            }
            velMas.addEventListener('click', () => { if (nivelVel < VELOCIDADES.length - 1) { nivelVel++; pintarVelocidad(); } });
            velMenos.addEventListener('click', () => { if (nivelVel > 0) { nivelVel--; pintarVelocidad(); } });
            pintarVelocidad();

            // La palabra que va más abajo es la que se acelera al tocar la pantalla
            function acelerarPalabra() {
                const activa = fallingWords.filter(f => !f.landed && !f.rapida)
                                           .sort((a, b) => b.y - a.y)[0];
                if (activa) activa.rapida = true;
            }

            // Margen a cada lado: así cualquier caja puede llegar al centro
            const svgPrincipal = document.getElementById('mainSvg');
            function ajustarMargen() {
                const margen = Math.round(scrollCont.clientWidth / 2);
                svgPrincipal.style.left = margen + 'px';
                wrapper.style.width = (900 + margen * 2) + 'px';
                return margen;
            }
            const margenInicial = ajustarMargen();
            // empezamos con el centro entre «Regular» y «Poco»
            scrollCont.scrollLeft = margenInicial + 437 - scrollCont.clientWidth / 2;""")
    s = cambiar(s, """                if (boosted) {
                    fallSpeed = FALL_SPEED_NORMAL;
                    boosted   = false;
                }
""", "")
    # las palabras caen desde el centro del cuadro (no de la ventana)
    s = cambiar(s, """                const x = window.innerWidth / 2 - w / 2;
                const scRect = scrollCont.getBoundingClientRect();""", """                const scRect = scrollCont.getBoundingClientRect();
                const x = scRect.left + scRect.width / 2 - w / 2;""")
    # tocar: no cuenta si se pulsa un botón
    s = cambiar(s, """            document.addEventListener('pointerdown', (e) => {
                pointerStartX    = e.clientX;""", """            document.addEventListener('pointerdown', (e) => {
                if (e.target.closest('button')) { isTap = false; return; }
                pointerStartX    = e.clientX;""")
    s = cambiar(s, """                if (isTap && elapsed < TAP_MAX_TIME) {
                    fallSpeed = FALL_SPEED_NORMAL * 5;
                    boosted   = true;
                }""", """                if (isTap && elapsed < TAP_MAX_TIME) {
                    acelerarPalabra();
                }""")
    s = cambiar(s, "                    fw.y += fallSpeed;", "                    fw.y += fw.rapida ? Math.max(fallSpeed, 1) * 5 : fallSpeed;")
    # --- teclado ---
    s = cambiar(s, """            scrollCont.addEventListener('wheel', e => {""", """            window.addEventListener('keydown', e => {
                if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                    // la flecha mueve las cajas en su dirección
                    scrollCont.scrollBy({ left: e.key === 'ArrowRight' ? -60 : 60, behavior: 'smooth' });
                    e.preventDefault();
                } else if (e.key === 'ArrowDown') {
                    acelerarPalabra();
                    e.preventDefault();
                }
            });
            window.addEventListener('resize', () => {
                const centro = scrollCont.scrollLeft + scrollCont.clientWidth / 2 - parseFloat(svgPrincipal.style.left || 0);
                const m = ajustarMargen();
                scrollCont.scrollLeft = m + centro - scrollCont.clientWidth / 2;
            });

            scrollCont.addEventListener('wheel', e => {""")
    # el clic final ya no debe acelerar nada; ocultar controles al terminar
    s = cambiar(s, """                    continueBtn.style.display = 'block';""", """                    continueBtn.style.display = 'block';
                    document.querySelector('.velocidad').style.display = 'none';""")
    open(ruta, "w", encoding="utf-8").write(s)
    print("ok", ruta)

for slug in ("2-examen", "2-examen-jovenes", "2-examen-primaria"):
    mejorar(os.path.join(RAIZ, slug, "index.html"))
