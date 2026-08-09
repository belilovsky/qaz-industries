/* QazGeo's reviewed static map renderer for QAZ.INDUSTRIES.
 * The browser consumes only the sanitized GeoJSON shipped with this release.
 * It never falls back to a decorative outline when the public contract fails. */
(function () {
  "use strict";

  var DATA_PATH = "data/qazgeo-regions-public.v1.geojson";
  var SCHEMA = "qaz-industries-qazgeo-regions-public-v1";
  var SOURCE_URL = "https://qgeo.tech/api/v1/mapregion/public/regions-geojson";
  var SVG_NS = "http://www.w3.org/2000/svg";
  var snapshotPromise;

  function assetUrl(path) {
    var marker = document.querySelector('meta[name="qaz-asset-version"]');
    var version = marker ? marker.getAttribute("content") || "source" : "source";
    return path + "?v=" + encodeURIComponent(version);
  }

  function setText(element, value) {
    if (element) element.textContent = value;
  }

  function setStatus(container, message, state) {
    var status = container.querySelector("[data-map-status]");
    setText(status, message);
    if (status) {
      status.classList.toggle("av-badge--success", state === "ready");
      status.classList.toggle("av-badge--danger", state === "error");
      status.classList.toggle("av-badge--info", state !== "error" && state !== "ready");
    }
  }

  function fetchSnapshot() {
    if (!snapshotPromise) {
      snapshotPromise = fetch(assetUrl(DATA_PATH), { credentials: "same-origin", cache: "no-store" })
        .then(function (response) {
          if (!response.ok) throw new Error("snapshot HTTP " + response.status);
          return response.json();
        })
        .then(function (payload) {
          if (!payload || payload.type !== "FeatureCollection" || payload.qaz_schema_version !== SCHEMA) {
            throw new Error("неверная схема QazGeo snapshot");
          }
          if (!Array.isArray(payload.features) || payload.features.length !== 20) {
            throw new Error("QazGeo snapshot должен содержать 20 регионов");
          }
          payload.features.forEach(function (feature) {
            if (!feature || !feature.geometry || !feature.properties || !feature.properties.code) {
              throw new Error("регион QazGeo без безопасной идентичности");
            }
          });
          return buildModel(payload);
        });
    }
    return snapshotPromise;
  }

  function collectPoints(node, output) {
    if (!Array.isArray(node)) return;
    if (node.length >= 2 && typeof node[0] === "number" && typeof node[1] === "number") {
      output.push([node[0], node[1]]);
      return;
    }
    node.forEach(function (child) { collectPoints(child, output); });
  }

  function projectPoint(point, bounds) {
    return [
      (point[0] - bounds.minX) * bounds.scale + bounds.offsetX,
      (bounds.maxY - point[1]) * bounds.scale + bounds.offsetY,
    ];
  }

  function pathForRing(ring, bounds) {
    if (!ring || ring.length < 3) return "";
    var first = projectPoint(ring[0], bounds);
    var path = "M " + first[0].toFixed(2) + " " + first[1].toFixed(2);
    for (var index = 1; index < ring.length; index += 1) {
      var point = projectPoint(ring[index], bounds);
      path += " L " + point[0].toFixed(2) + " " + point[1].toFixed(2);
    }
    return path + " Z";
  }

  function pathForGeometry(geometry, bounds) {
    if (geometry.type === "Polygon") {
      return geometry.coordinates.map(function (ring) { return pathForRing(ring, bounds); }).join(" ");
    }
    if (geometry.type === "MultiPolygon") {
      return geometry.coordinates.map(function (polygon) {
        return polygon.map(function (ring) { return pathForRing(ring, bounds); }).join(" ");
      }).join(" ");
    }
    throw new Error("неподдерживаемая геометрия QazGeo: " + geometry.type);
  }

  function buildModel(payload) {
    var points = [];
    payload.features.forEach(function (feature) { collectPoints(feature.geometry.coordinates, points); });
    if (!points.length) throw new Error("QazGeo snapshot не содержит координат");
    var minX = Math.min.apply(null, points.map(function (point) { return point[0]; }));
    var maxX = Math.max.apply(null, points.map(function (point) { return point[0]; }));
    var minY = Math.min.apply(null, points.map(function (point) { return point[1]; }));
    var maxY = Math.max.apply(null, points.map(function (point) { return point[1]; }));
    var padding = 30;
    var width = 1000;
    var height = 560;
    var scale = Math.min((width - padding * 2) / Math.max(maxX - minX, 0.1), (height - padding * 2) / Math.max(maxY - minY, 0.1));
    var bounds = {
      minX: minX,
      maxY: maxY,
      scale: scale,
      offsetX: (width - (maxX - minX) * scale) / 2,
      offsetY: (height - (maxY - minY) * scale) / 2,
    };
    return {
      source: payload.source || SOURCE_URL,
      features: payload.features.map(function (feature) {
        var properties = feature.properties;
        return {
          id: String(properties.code),
          name: String(properties.name_ru || properties.code),
          nameEn: String(properties.name_en || properties.code),
          type: String(properties.region_type || "region"),
          path: pathForGeometry(feature.geometry, bounds),
        };
      }),
    };
  }

  function svgElement(name) {
    return document.createElementNS(SVG_NS, name);
  }

  function updateInspector(container, feature) {
    var inspector = container.querySelector("[data-map-inspector]");
    if (!inspector) return;
    if (!feature) {
      setText(inspector, "Выберите регион, чтобы увидеть его код и тип.");
      return;
    }
    setText(inspector, feature.name + " · " + feature.id + " · " + feature.type);
  }

  function renderMap(container, model) {
    var svg = container.querySelector("[data-map-svg]");
    if (!svg) return;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    svg.setAttribute("viewBox", "0 0 1000 560");
    svg.setAttribute("aria-label", "Реальные границы регионов Казахстана из QazGeo");
    var viewport = svgElement("g");
    viewport.setAttribute("class", "qazgeo-map__viewport");
    svg.appendChild(viewport);
    var selected;
    var scale = 1;
    var zoomOut = container.querySelector("[data-map-zoom-out]");
    var zoomIn = container.querySelector("[data-map-zoom-in]");
    var zoomReset = container.querySelector("[data-map-zoom-reset]");

    function updateZoom() {
      viewport.setAttribute("transform", "translate(500 280) scale(" + scale + ") translate(-500 -280)");
      if (zoomOut) zoomOut.disabled = scale <= 1;
      if (zoomIn) zoomIn.disabled = scale >= 2.5;
      if (zoomReset) zoomReset.disabled = scale === 1;
    }

    function select(feature, path) {
      if (selected) selected.classList.remove("is-selected");
      selected = path;
      if (selected) selected.classList.add("is-selected");
      updateInspector(container, feature);
    }

    model.features.forEach(function (feature) {
      var path = svgElement("path");
      path.setAttribute("class", "map-region");
      path.setAttribute("d", feature.path);
      path.setAttribute("fill-rule", "evenodd");
      path.setAttribute("clip-rule", "evenodd");
      path.setAttribute("data-region-code", feature.id);
      path.setAttribute("tabindex", "0");
      path.setAttribute("role", "button");
      path.setAttribute("aria-label", feature.name + " (" + feature.id + ")");
      var title = svgElement("title");
      title.textContent = feature.name + " · " + feature.id;
      path.appendChild(title);
      path.addEventListener("click", function () { select(feature, path); });
      path.addEventListener("focus", function () { select(feature, path); });
      path.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          select(feature, path);
        }
      });
      viewport.appendChild(path);
    });

    if (zoomOut) zoomOut.addEventListener("click", function () { scale = Math.max(1, Number((scale - 0.25).toFixed(2))); updateZoom(); });
    if (zoomIn) zoomIn.addEventListener("click", function () { scale = Math.min(2.5, Number((scale + 0.25).toFixed(2))); updateZoom(); });
    if (zoomReset) zoomReset.addEventListener("click", function () { scale = 1; updateZoom(); });
    updateZoom();
    updateInspector(container);
    setStatus(container, "QazGeo · " + model.features.length + " реальных границ · reviewed snapshot", "ready");
    var source = container.querySelector("[data-map-source]");
    if (source) source.href = model.source || SOURCE_URL;
  }

  function renderError(container, error) {
    setStatus(container, "QazGeo snapshot недоступен · карта скрыта", "error");
    var inspector = container.querySelector("[data-map-inspector]");
    setText(inspector, "Карта не подменяется декоративной схемой. Обновите выпуск или откройте источник QazGeo.");
    var svg = container.querySelector("[data-map-svg]");
    if (svg) while (svg.firstChild) svg.removeChild(svg.firstChild);
    if (window.console && console.error) console.error("QazGeo map:", error);
  }

  function init() {
    var maps = document.querySelectorAll("[data-qazgeo-map]");
    if (!maps.length) return;
    Array.prototype.forEach.call(maps, function (container) {
      setStatus(container, "Загружаем QazGeo snapshot…", "loading");
      fetchSnapshot().then(function (model) { renderMap(container, model); }).catch(function (error) { renderError(container, error); });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
}());
