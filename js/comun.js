/* yomeconfieso.es — pequeñas funciones comunes a todas las páginas */
(function () {
  "use strict";
  function guardar(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function leer(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  // 1) Recordar la versión del examen (adultos, jóvenes, chicos/as) para que «Examen de conciencia»
  //    en el camino lleve siempre a la misma versión.
  var m = /\/(2-examen|3-preguntas)(-jovenes|-primaria)?\//.exec(location.pathname);
  if (m) guardar("variante", m[2] || "");
  var variante = leer("variante");
  if (variante) {
    document.querySelectorAll('a[data-parte="1"]').forEach(function (a) {
      a.setAttribute("href", a.getAttribute("href").replace(/2-examen(-jovenes|-primaria)?\//, "2-examen" + variante + "/"));
    });
  }

  // 2) Vídeos «Para profundizar»: se cargan solo al abrirlos
  document.querySelectorAll("details.yc-video").forEach(function (d) {
    d.addEventListener("toggle", function () {
      var f = d.querySelector("iframe");
      if (!f) return;
      if (d.open) { if (!f.getAttribute("src")) f.setAttribute("src", f.getAttribute("data-src")); }
      else f.removeAttribute("src");
    });
  });

  // 3) Propósito de la enmienda: se guarda en el dispositivo y se muestra al final
  var campo = document.getElementById("proposito");
  if (campo) {
    campo.value = leer("proposito") || "";
    campo.addEventListener("input", function () { guardar("proposito", campo.value.trim()); });
  }
  var caja = document.getElementById("mi-proposito-caja");
  var texto = leer("proposito");
  if (caja && texto) {
    document.getElementById("mi-proposito").textContent = texto;
    caja.hidden = false;
  }
})();
