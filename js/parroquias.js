/* yomeconfieso.es — Parroquias católicas cercanas.
   1) Busca al momento en Photon (OpenStreetMap) y filtra por nombre.
   2) En segundo plano consulta Overpass (OpenStreetMap) para afinar:
      quita las que estén marcadas como no católicas y añade las católicas que falten.
   Cada resultado enlaza a Google Maps con la ruta a pie desde la posición del usuario. */
(function () {
  "use strict";

  var RADIO_KM = 15;
  var MAX_RESULTADOS = 10;
  var NO_CATOLICA = /evang[eé]l|pentecost|cristian|b[ií]blic|testigos|jehov|adventist|bautist|protestant|ortodox|morm[oó]n|[uú]ltimos d[ií]as|anglican|luteran|metodist|presbiterian|sal[oó]n del reino|asamblea|filadelfia|apost[oó]lic|nueva vida|iglesia de dios|ministerio|reformad|sinagoga|mezquita|budist|hind[uú]|sikh|cienciolog/i;
  var CATOLICA_NOMBRE = /parroqui|iglesia|templo|catedral|bas[ií]lica|ermita|santuario|capilla|convento|monasterio|colegiata|oratorio|cartuja|abad[ií]a|san |santa |santo |sant |nuestra se[ñn]ora|virgen|cristo|sagrad|esp[ií]ritu santo|trinidad|asunci[oó]n|inmaculada|pilar|merced|carmen/i;
  var DENOM_CATOLICA = /^(catholic|roman_catholic)$/;

  var estado = { lat: null, lon: null, lista: [], contenedor: null };

  function distancia(lat1, lon1, lat2, lon2) {
    var R = 6371000, rad = function (x) { return x * Math.PI / 180; };
    var dLat = rad(lat2 - lat1), dLon = rad(lon2 - lon1);
    var a = Math.pow(Math.sin(dLat / 2), 2) + Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.pow(Math.sin(dLon / 2), 2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }
  function textoDistancia(m) {
    return m < 1000 ? Math.round(m / 10) * 10 + " m" : (m / 1000).toFixed(1).replace(".", ",") + " km";
  }
  function nombreValido(n) { return !!n && CATOLICA_NOMBRE.test(n) && !NO_CATOLICA.test(n); }
  function mensaje(t) { estado.contenedor.innerHTML = ""; var p = document.createElement("p"); p.className = "parroquias-mensaje"; p.textContent = t; estado.contenedor.appendChild(p); }

  function pintar() {
    var c = estado.contenedor;
    var lista = estado.lista.slice().sort(function (a, b) { return a.dist - b.dist; }).slice(0, MAX_RESULTADOS);
    if (!lista.length) { mensaje("No hemos encontrado parroquias católicas cerca. Prueba a buscar «parroquia» en Google Maps."); return; }
    c.innerHTML = "";
    lista.forEach(function (p) {
      var item = document.createElement("div");
      item.className = "parroquia-item";
      var cab = document.createElement("div");
      cab.className = "parroquia-header";
      var nom = document.createElement("span"); nom.className = "nombre"; nom.textContent = p.nombre;
      var dis = document.createElement("span"); dis.className = "distancia"; dis.textContent = textoDistancia(p.dist);
      cab.appendChild(nom); cab.appendChild(dis);
      item.appendChild(cab);
      if (p.dir) { var d = document.createElement("span"); d.className = "parroquia-dir"; d.textContent = p.dir; item.appendChild(d); }
      var a = document.createElement("a");
      a.className = "parroquia-ruta";
      a.target = "_blank";
      a.rel = "noopener";
      a.href = "https://www.google.com/maps/dir/?api=1&origin=" + estado.lat + "," + estado.lon +
               "&destination=" + p.lat + "," + p.lon + "&travelmode=" + (p.dist < 2500 ? "walking" : "driving");
      a.textContent = "Cómo llegar en Google Maps";
      item.appendChild(a);
      c.appendChild(item);
    });
    var nota = document.createElement("p");
    nota.className = "parroquias-nota";
    nota.textContent = "Datos de OpenStreetMap. Comprueba los horarios de confesión en la propia parroquia.";
    c.appendChild(nota);
  }

  function clave(tipo, id) { return (tipo || "").charAt(0).toUpperCase() + id; }

  function buscarPhoton() {
    var terminos = ["parroquia", "iglesia", "ermita"];
    return Promise.all(terminos.map(function (q) {
      var url = "https://photon.komoot.io/api/?q=" + encodeURIComponent(q) + "&lat=" + estado.lat + "&lon=" + estado.lon +
                "&limit=40&osm_tag=amenity:place_of_worship";
      return fetch(url).then(function (r) { return r.json(); }).catch(function () { return { features: [] }; });
    })).then(function (respuestas) {
      var vistos = {};
      respuestas.forEach(function (r) {
        (r.features || []).forEach(function (f) {
          var pr = f.properties || {}, co = (f.geometry || {}).coordinates || [];
          if (!nombreValido(pr.name) || co.length < 2) return;
          var k = clave(pr.osm_type, pr.osm_id);
          if (vistos[k]) return;
          var dist = distancia(estado.lat, estado.lon, co[1], co[0]);
          if (dist > RADIO_KM * 1000) return;
          vistos[k] = true;
          var dir = [pr.street && (pr.street + (pr.housenumber ? " " + pr.housenumber : "")), pr.city || pr.town || pr.village].filter(Boolean).join(", ");
          estado.lista.push({ k: k, nombre: pr.name, lat: co[1], lon: co[0], dist: dist, dir: dir });
        });
      });
    });
  }

  function afinarOverpass() {
    var R = 6000;
    var q = '[out:json][timeout:40];nwr["amenity"="place_of_worship"]["religion"="christian"](around:' + R + "," + estado.lat + "," + estado.lon + ");out center tags;";
    var servidores = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"];
    function intentar(i) {
      if (i >= servidores.length) return Promise.reject(new Error("sin servidor"));
      var ctrl = window.AbortController ? new AbortController() : null;
      var t = setTimeout(function () { if (ctrl) ctrl.abort(); }, 45000);
      return fetch(servidores[i], {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "data=" + encodeURIComponent(q),
        signal: ctrl ? ctrl.signal : undefined
      }).then(function (r) { clearTimeout(t); if (!r.ok) throw new Error(r.status); return r.json(); })
        .catch(function () { clearTimeout(t); return intentar(i + 1); });
    }
    return intentar(0).then(function (j) {
      var noCatolicas = {}, enLista = {};
      estado.lista.forEach(function (p) { enLista[p.k] = true; });
      (j.elements || []).forEach(function (e) {
        var t = e.tags || {}, k = clave(e.type, e.id);
        var den = t.denomination;
        if (den && !DENOM_CATOLICA.test(den)) { noCatolicas[k] = true; return; }
        if (enLista[k]) return;
        var catolica = (den && DENOM_CATOLICA.test(den)) || nombreValido(t.name);
        if (!catolica || !t.name || (t.name && NO_CATOLICA.test(t.name))) return;
        var lat = e.lat || (e.center && e.center.lat), lon = e.lon || (e.center && e.center.lon);
        if (!lat || !lon) return;
        var dir = [t["addr:street"] && (t["addr:street"] + (t["addr:housenumber"] ? " " + t["addr:housenumber"] : "")), t["addr:city"]].filter(Boolean).join(", ");
        estado.lista.push({ k: k, nombre: t.name, lat: lat, lon: lon, dist: distancia(estado.lat, estado.lon, lat, lon), dir: dir });
      });
      estado.lista = estado.lista.filter(function (p) { return !noCatolicas[p.k]; });
    });
  }

  window.listarParroquias = function () {
    estado.contenedor = document.getElementById("parroquias");
    if (!estado.contenedor) return;
    if (!navigator.geolocation) { mensaje("Tu navegador no permite saber tu ubicación."); return; }
    mensaje("Buscando tu ubicación…");
    navigator.geolocation.getCurrentPosition(function (pos) {
      estado.lat = pos.coords.latitude;
      estado.lon = pos.coords.longitude;
      estado.lista = [];
      mensaje("Buscando parroquias católicas cercanas…");
      buscarPhoton().then(function () {
        if (estado.lista.length) pintar(); else mensaje("Buscando parroquias católicas cercanas… (un momento)");
        return afinarOverpass().then(pintar, function () { if (!estado.lista.length) pintar(); });
      });
    }, function (err) {
      if (err && err.code === 1) mensaje("Para ver las parroquias cercanas, permite el acceso a tu ubicación en el navegador y vuelve a abrir esta pestaña.");
      else mensaje("No hemos podido obtener tu ubicación. Inténtalo de nuevo en un momento.");
    }, { enableHighAccuracy: false, timeout: 15000, maximumAge: 300000 });
  };
})();
