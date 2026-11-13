/* yomeconfieso.es — Selección de cartas y elección de sistema en la página del examen.
   Cada página de examen define antes:
     window.PALABRAS_EXAMEN   = [ ...palabras... ]
     window.DESTINO_PREGUNTAS = "../3-preguntas/"
   Guarda el resultado igual que el juego de caída: localStorage.resultados = [{word, value}] */
(function () {
  "use strict";

  var DESCRIPCIONES = {
    // Adultos
    "Sin rezar": "Dejar la oración o rezar con desgana.",
    "Superstición": "Horóscopos, amuletos, buscar la suerte fuera de Dios.",
    "Sin Misa": "Faltar a Misa el domingo o comulgar sin estar preparado.",
    "Blasfemia": "Insultar o burlarse de Dios y de lo sagrado.",
    "Soberbia": "Creerme por encima de los demás y querer quedar siempre bien.",
    "Desobediencia": "No obedecer a quien tiene autoridad sobre mí.",
    "Contestaciones": "Responder mal o con desprecio a quien me corrige.",
    "Aborto": "Abortar, usar abortivos o colaborar en un aborto.",
    "Odio": "Guardar rencor, desear el mal o negarme a perdonar.",
    "Ira": "Enfados, gritos, insultos o violencia.",
    "Crítica": "Juzgar con dureza o hablar mal de los demás.",
    "Chisme": "Cotillear o difundir defectos ajenos.",
    "Bullying": "Humillar, acosar o burlarme de alguien.",
    "Xenofobia": "Despreciar o discriminar por origen, raza o religión.",
    "Drogas": "Consumir drogas o facilitarlas a otros.",
    "Embriaguez": "Beber en exceso o emborracharme.",
    "Gula": "Comer, beber o consumir sin medida, también pantallas.",
    "Pornografía": "Buscar o ver imágenes o vídeos sexuales.",
    "Impureza": "Actos impuros, a solas o con otros.",
    "Sexo": "Relaciones fuera del matrimonio o infidelidad.",
    "Robo": "Quedarme con lo ajeno o no ser honrado.",
    "Avaricia": "Apego al dinero; no compartir pudiendo hacerlo.",
    "Materialista": "Gastar sin necesidad, vivir para tener cosas.",
    "Egoísmo": "Pensar solo en mí y usar a los demás.",
    "Pereza": "Dejar para luego lo importante, hacer las cosas mal.",
    "Mentira": "Engañar, fingir o esconder la verdad.",
    "Envidia": "Entristecerme por el bien de otros o alegrarme de su mal.",
    // Jóvenes
    "Sin Dios": "Dudar de la fe o acordarme de Dios solo cuando lo necesito.",
    "Idolatría": "Poner personas, cosas o supersticiones por delante de Dios.",
    "Irreverencia": "Usar el nombre de Dios sin respeto o jurar sin necesidad.",
    "Irrespetuoso con Dios": "Ir a Misa o comulgar distraído y sin respeto.",
    "Irrespetuoso con otros": "No respetar a la autoridad ni cumplir con estudio o trabajo.",
    "Violento": "Herir, insultar o desear el mal a alguien.",
    "Imprudente": "Poner en peligro mi vida o la de otros.",
    "Calumnia": "Hablar mal de otros, chismes o juicios precipitados.",
    "Impureza mental": "Consentir pensamientos o deseos impuros.",
    "Falta de respeto": "No tratar con respeto a las personas del otro sexo.",
    "Codicia": "Desear lo que no me pertenece, ambición desordenada.",
    // Chicos y chicas
    "NO REZO": "Me olvido de rezar o rezo poco.",
    "BLASFEMIA": "Digo palabras feas con las cosas de Dios.",
    "SIN MISA": "No voy a Misa aunque podía ir.",
    "DESOBEDIENCIA": "No hago caso a mis padres o profesores.",
    "NO RESPETAR": "Falto al respeto a otras personas.",
    "HABLAR MAL": "Hablo mal de otros cuando no están.",
    "PELEAS": "Me peleo con mis hermanos o amigos.",
    "BURLAS": "Me río de otros o los dejo en ridículo.",
    "ENFADOS": "Me enfado a menudo.",
    "NO PERDONO": "No perdono o no pido perdón.",
    "RENCOROSO/A": "Me guardo el enfado y no olvido.",
    "ORGULLOSO/A": "Me molesta que me corrijan.",
    "QUEJAS": "Me quejo mucho de todo.",
    "IMPUREZA": "Veo, digo o hago cosas impuras.",
    "PEREZA": "No hago lo que no me apetece.",
    "EGOÍSTA": "No comparto mis cosas ni mi tiempo.",
    "ME LO QUEDO": "Cojo cosas que no son mías.",
    "CAPRICHOSO": "Siempre quiero tener más.",
    "MENTIROSO": "Digo mentiras o engaño.",
    "ENVIDIOSO": "Me da envidia lo que tienen otros.",
    "CABEZOTA": "Quiero tener siempre la razón."
  };

  var CESTAS = [
    { id: "mucho", nombre: "Mucho", valor: 3 },
    { id: "regular", nombre: "Regular", valor: 2 },
    { id: "poco", nombre: "Poco", valor: 1 }
  ];

  function el(tag, attrs, hijos) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "text") e.textContent = attrs[k];
      else if (k === "html") e.innerHTML = attrs[k];
      else e.setAttribute(k, attrs[k]);
    });
    (hijos || []).forEach(function (h) { if (h) e.appendChild(h); });
    return e;
  }

  function vibrar(ms) { try { if (navigator.vibrate) navigator.vibrate(ms); } catch (e) {} }

  function nombreBonito(p) {
    // Las palabras de chicos/as vienen en mayúsculas: se muestran en tipo frase
    if (p === p.toUpperCase()) return p.charAt(0) + p.slice(1).toLowerCase();
    return p;
  }

  /* =================== SELECCIÓN DE CARTAS =================== */
  function iniciarCartas(raiz) {
    var palabras = (window.PALABRAS_EXAMEN || []).slice();
    var destino = window.DESTINO_PREGUNTAS || "../3-preguntas/";
    var resultados = [];
    var indice = 0;

    raiz.innerHTML = "";
    raiz.hidden = false;

    var contador = el("span", { class: "cartas-contador" });
    var deshacer = el("button", { type: "button", class: "cartas-deshacer", text: "Deshacer" });

    var pista = el("p", { class: "cartas-pista", html: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg> <span>Arriba: <strong>nada</strong></span>' });
    var mesa = el("div", { class: "cartas-mesa" });
    var cestasCaja = el("div", { class: "cartas-cestas" });
    var cestasEls = {};
    CESTAS.forEach(function (c) {
      var n = el("span", { class: "cesta-num", text: "0" });
      var b = el("div", { class: "cesta cesta-" + c.id, "data-cesta": c.id }, [el("span", { class: "cesta-nombre", text: c.nombre }), n]);
      cestasEls[c.id] = { caja: b, num: n, total: 0 };
      cestasCaja.appendChild(b);
    });
    var botones = el("div", { class: "cartas-botones", "aria-label": "O elige con un toque" });
    CESTAS.concat([{ id: "nada", nombre: "Nada", valor: 0 }]).forEach(function (c) {
      var b = el("button", { type: "button", class: "cartas-boton boton-" + c.id, text: c.nombre });
      b.addEventListener("click", function () { decidir(c.id); });
      botones.appendChild(b);
    });
    var teclado = el("p", { class: "cartas-teclado", text: "Teclado: ← Mucho · ↓ Regular · → Poco · ↑ Nada" });
    var final = el("div", { class: "cartas-final", hidden: "" });

    var cabecera = el("div", { class: "cartas-cabecera" }, [contador, pista, deshacer]);
    raiz.appendChild(mesa);
    raiz.appendChild(cabecera);
    raiz.appendChild(cestasCaja);
    raiz.appendChild(botones);
    raiz.appendChild(teclado);
    raiz.appendChild(final);

    var carta = null;
    var ocupado = false;

    function actualizar() {
      contador.textContent = Math.min(indice + 1, palabras.length) + " / " + palabras.length;
      deshacer.disabled = resultados.length === 0 || ocupado;
    }

    function nuevaCarta() {
      mesa.innerHTML = "";
      // cartas de fondo (el montón)
      var quedan = palabras.length - indice;
      if (quedan > 2) mesa.appendChild(el("div", { class: "carta carta-fondo fondo-2", "aria-hidden": "true" }));
      if (quedan > 1) {
        var sig = palabras[indice + 1];
        mesa.appendChild(el("div", { class: "carta carta-fondo carta-siguiente", "aria-hidden": "true" }, [
          el("span", { class: "carta-palabra", text: nombreBonito(sig) }),
          el("span", { class: "carta-desc", text: DESCRIPCIONES[sig] || "" })
        ]));
      }
      if (indice >= palabras.length) { terminar(); return; }
      var p = palabras[indice];
      carta = el("div", { class: "carta carta-activa entrando", role: "group", "aria-label": nombreBonito(p) }, [
        el("span", { class: "carta-etiqueta" }),
        el("span", { class: "carta-palabra", text: nombreBonito(p) }),
        el("span", { class: "carta-desc", text: DESCRIPCIONES[p] || "" })
      ]);
      mesa.appendChild(carta);
      requestAnimationFrame(function () { requestAnimationFrame(function () { carta.classList.remove("entrando"); }); });
      prepararArrastre(carta);
      actualizar();
    }

    function centro(r) { return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }

    function cestaBajo(x, y) {
      var mejor = null, dist = Infinity;
      CESTAS.forEach(function (c) {
        var r = cestasEls[c.id].caja.getBoundingClientRect();
        var cc = centro(r);
        var d = Math.hypot(x - cc.x, y - cc.y);
        if (d < dist) { dist = d; mejor = c.id; }
      });
      var rCaja = cestasCaja.getBoundingClientRect();
      // solo cuenta si estamos cerca de la fila de cestas
      return y > rCaja.top - 110 ? mejor : null;
    }

    function marcarCesta(id) {
      CESTAS.forEach(function (c) { cestasEls[c.id].caja.classList.toggle("encima", c.id === id); });
      var etq = carta && carta.querySelector(".carta-etiqueta");
      if (etq) {
        var c = CESTAS.filter(function (x) { return x.id === id; })[0];
        etq.textContent = c ? c.nombre : "";
        carta.setAttribute("data-encima", id || "");
      }
    }

    function prepararArrastre(c) {
      var inicio = null;
      var rMesa0 = null;
      c.addEventListener("pointerdown", function (e) {
        if (ocupado) return;
        inicio = { x: e.clientX, y: e.clientY };
        rMesa0 = centro(c.getBoundingClientRect());
        c.setPointerCapture(e.pointerId);
        c.classList.add("arrastrando");
      });
      c.addEventListener("pointermove", function (e) {
        if (!inicio) return;
        var dx = e.clientX - inicio.x, dy = e.clientY - inicio.y;
        var yCestas = centro(cestasCaja.getBoundingClientRect()).y;
        // cuanto más cerca de las cestas, más pequeña
        var progreso = Math.max(0, Math.min(1, dy / Math.max(1, yCestas - rMesa0.y)));
        var escala = 1 - 0.9 * progreso;
        var opacidad = dy < 0 ? Math.max(0.25, 1 + dy / 260) : 1;
        c.style.transform = "translate(" + dx + "px," + dy + "px) rotate(" + Math.max(-40, Math.min(40, dx * 0.18 + dy * 0.04 * (dx < 0 ? -1 : 1))) + "deg) scale(" + escala + ")";
        c.style.opacity = opacidad;
        marcarCesta(cestaBajo(e.clientX, e.clientY));
        pista.classList.toggle("activa", dy < -60);
      });
      function soltar(e) {
        if (!inicio) return;
        var dy = e.clientY - inicio.y;
        var id = cestaBajo(e.clientX, e.clientY);
        inicio = null;
        c.classList.remove("arrastrando");
        pista.classList.remove("activa");
        if (id) decidir(id);
        else if (dy < -110) decidir("nada");
        else {
          c.style.transform = "";
          c.style.opacity = "";
          marcarCesta(null);
        }
      }
      c.addEventListener("pointerup", soltar);
      c.addEventListener("pointercancel", soltar);
    }

    function decidir(id) {
      if (ocupado || !carta || indice >= palabras.length) return;
      ocupado = true;
      var valor = id === "nada" ? 0 : CESTAS.filter(function (x) { return x.id === id; })[0].valor;
      var palabra = palabras[indice];
      var c = carta;
      marcarCesta(id === "nada" ? null : id);
      c.classList.add("volando");
      var rc = c.getBoundingClientRect();
      var cc = centro(rc);
      var actual = c.style.transform || "";
      var dx0 = 0, dy0 = 0;
      var m = /translate\(([-\d.]+)px,\s*([-\d.]+)px\)/.exec(actual);
      if (m) { dx0 = parseFloat(m[1]); dy0 = parseFloat(m[2]); }
      if (id === "nada") {
        c.style.transform = "translate(" + dx0 + "px," + (dy0 - window.innerHeight) + "px) rotate(" + (dx0 * 0.2) + "deg) scale(0.8)";
        c.style.opacity = "0";
      } else {
        var cb = centro(cestasEls[id].caja.getBoundingClientRect());
        c.style.transform = "translate(" + (dx0 + cb.x - cc.x) + "px," + (dy0 + cb.y - cc.y) + "px) rotate(" + (dx0 >= 0 ? 25 : -25) + "deg) scale(0.06)";
        c.style.opacity = "0.2";
      }
      vibrar(id === "nada" ? 8 : 18);
      setTimeout(function () {
        resultados.push({ word: palabra, value: valor, cesta: id });
        if (id !== "nada") {
          var ce = cestasEls[id];
          ce.total++;
          ce.num.textContent = ce.total;
          ce.caja.classList.remove("pulso");
          void ce.caja.offsetWidth;
          ce.caja.classList.add("pulso");
        }
        marcarCesta(null);
        indice++;
        ocupado = false;
        nuevaCarta();
      }, 280);
    }

    deshacer.addEventListener("click", function () {
      if (ocupado || !resultados.length) return;
      var ultimo = resultados.pop();
      if (ultimo.cesta !== "nada") {
        var ce = cestasEls[ultimo.cesta];
        ce.total--;
        ce.num.textContent = ce.total;
      }
      indice--;
      final.hidden = true;
      mesa.hidden = false; cestasCaja.hidden = false; botones.hidden = false; pista.hidden = false;
      nuevaCarta();
    });

    function terminar() {
      carta = null;
      localStorage.setItem("resultados", JSON.stringify(resultados.map(function (r) { return { word: r.word, value: r.value }; })));
      vibrar([20, 40, 20]);
      setTimeout(function () { if (window.finExamen) window.finExamen(); }, 350);
    }

    window.addEventListener("keydown", function (e) {
      if (raiz.hidden || ocupado) return;
      var mapa = { ArrowLeft: "mucho", ArrowDown: "regular", ArrowRight: "poco", ArrowUp: "nada" };
      if (mapa[e.key] && indice < palabras.length) { decidir(mapa[e.key]); e.preventDefault(); }
    });

    nuevaCarta();
  }

  /* =================== VENTANA PARA ELEGIR SISTEMA =================== */
  var DIBUJO_CAIDA =
    '<svg viewBox="0 0 160 110" aria-hidden="true"><rect x="1" y="1" width="158" height="108" rx="14" fill="#fff" stroke="#E4DEEC"/>' +
    '<rect x="58" y="14" width="44" height="14" rx="5" fill="#ECE8F3"/><rect x="62" y="44" width="36" height="14" rx="5" fill="#ECE8F3"/>' +
    '<path d="M80 30v8M80 60v8" stroke="#9A91B5" stroke-width="2" stroke-linecap="round" stroke-dasharray="2 4"/>' +
    '<rect x="10" y="80" width="40" height="20" rx="6" fill="#9E3B52"/><rect x="60" y="80" width="40" height="20" rx="6" fill="#C7843A"/>' +
    '<rect x="110" y="80" width="40" height="20" rx="6" fill="#5E8F6E"/></svg>';
  var DIBUJO_CARTAS =
    '<svg viewBox="0 0 160 110" aria-hidden="true"><rect x="1" y="1" width="158" height="108" rx="14" fill="#fff" stroke="#E4DEEC"/>' +
    '<rect x="56" y="12" width="48" height="58" rx="8" fill="#F7F4EF" stroke="#E4DEEC" transform="rotate(-6 80 41)"/>' +
    '<g transform="rotate(10 92 44)"><rect x="66" y="14" width="48" height="58" rx="8" fill="#fff" stroke="#C7843A" stroke-width="2"/>' +
    '<rect x="76" y="34" width="28" height="7" rx="3" fill="#2A2238"/><rect x="74" y="46" width="32" height="4" rx="2" fill="#CFC7DD"/></g>' +
    '<circle cx="40" cy="92" r="12" fill="none" stroke="#9E3B52" stroke-width="2" stroke-dasharray="3 3"/>' +
    '<circle cx="80" cy="92" r="14" fill="#C7843A"/><circle cx="120" cy="92" r="12" fill="none" stroke="#5E8F6E" stroke-width="2" stroke-dasharray="3 3"/></svg>';

  function abrirEleccion(alElegir) {
    var fondo = el("div", { class: "eleccion-fondo", role: "dialog", "aria-modal": "true", "aria-labelledby": "eleccion-titulo" });
    var caja = el("div", { class: "eleccion-caja" });
    caja.appendChild(el("p", { class: "eleccion-ante", text: "Antes de empezar" }));
    caja.appendChild(el("h2", { id: "eleccion-titulo", text: "¿Cómo quieres hacer el examen?" }));
    var opciones = el("div", { class: "eleccion-opciones" });
    [
      { id: "caida", titulo: "Juego de selección", texto: "Las palabras caen y tú mueves las cajas.", dibujo: DIBUJO_CAIDA },
      { id: "cartas", titulo: "Selección de cartas", texto: "Una carta cada vez: arrástrala a su cesta.", dibujo: DIBUJO_CARTAS }
    ].forEach(function (o) {
      var b = el("button", { type: "button", class: "eleccion-opcion", "data-sistema": o.id });
      b.innerHTML = o.dibujo + '<strong>' + o.titulo + '</strong><span>' + o.texto + '</span>';
      b.addEventListener("click", function () {
        try { localStorage.setItem("sistemaExamen", o.id); } catch (e) {}
        document.body.classList.remove("eleccion-abierta");
        fondo.remove();
        alElegir(o.id);
      });
      opciones.appendChild(b);
    });
    caja.appendChild(opciones);
    fondo.appendChild(caja);
    document.body.appendChild(fondo);
    document.body.classList.add("eleccion-abierta");
    var previa = null;
    try { previa = localStorage.getItem("sistemaExamen"); } catch (e) {}
    caja.setAttribute("tabindex", "-1");
    caja.focus();
  }

  /* =================== VENTANA DEL JUEGO =================== */
  function abrirModal() {
    var m = document.getElementById("juegoModal");
    if (!m) return;
    m.hidden = false;
    m.classList.remove("saliendo");
    document.body.classList.add("juego-abierto");
    var c = m.querySelector(".juego-modal-cuerpo");
    if (c) c.scrollTop = 0;
  }
  function cerrarModal(fundido, despues) {
    var m = document.getElementById("juegoModal");
    if (!m) return;
    function fin() {
      m.hidden = true;
      m.classList.remove("saliendo");
      document.body.classList.remove("juego-abierto");
      if (despues) despues();
    }
    if (fundido) { m.classList.add("saliendo"); setTimeout(fin, 650); } else fin();
  }
  window.finExamen = function () {
    cerrarModal(true, function () {
      // El texto de presentación se queda; solo se oculta el botón «Comenzar»
      var empezar = document.getElementById("empezarExamen");
      var fin = document.getElementById("finExamen");
      if (empezar) empezar.hidden = true;
      if (fin) {
        fin.hidden = false;
        fin.classList.add("apareciendo");
        setTimeout(function () { fin.scrollIntoView({ behavior: "smooth", block: "center" }); }, 50);
      }
    });
  };

  function preparar() {
    var inicio = document.getElementById("startScreen");
    var cartas = document.getElementById("cartas");
    var empezar = document.getElementById("empezarExamen");
    var cerrar = document.getElementById("cerrarJuego");
    var repetir = document.getElementById("repetirExamen");
    if (!inicio || !cartas || !empezar) return;
    var juegoEmpezado = false;
    function elegir(sistema) {
      abrirModal();
      if (sistema === "cartas") {
        inicio.style.display = "none";
        iniciarCartas(cartas);
      } else {
        cartas.hidden = true;
        // directamente al juego, sin la pantalla de instrucciones
        if (!juegoEmpezado) {
          inicio.style.display = "none";
          var b = document.getElementById("startBtn");
          if (b) b.click();
        }
      }
    }
    empezar.addEventListener("click", function () {
      if (juegoEmpezado) { abrirModal(); return; }
      abrirEleccion(elegir);
    });
    var btnJuego = document.getElementById("startBtn");
    if (btnJuego) btnJuego.addEventListener("click", function () { juegoEmpezado = true; });
    if (cerrar) cerrar.addEventListener("click", function () {
      cerrarModal(false);
      empezar.textContent = juegoEmpezado || !cartas.hidden ? "Continuar" : "Comenzar";
    });
    if (repetir) repetir.addEventListener("click", function () { location.reload(); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", preparar);
  else preparar();
})();
