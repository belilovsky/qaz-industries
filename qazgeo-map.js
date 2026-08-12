/* QazGeo map renderer for the reviewed QAZ.INDUSTRIES release asset.
 * The browser consumes only the sanitized GeoJSON shipped with this release.
 * It never falls back to a decorative outline when the public contract fails. */
(function () {
  "use strict";

  var DATA_PATH = "data/qazgeo-regions-public.v1.geojson";
  var SOURCE_URL = "https://qgeo.tech/api/v1/mapregion/public/regions-geojson";
  var SVG_NS = "http://www.w3.org/2000/svg";
  var snapshotPromise;
  var runtime = window.QAZ_RUNTIME;
  var contracts = window.QAZ_SNAPSHOT_CONTRACTS;
  var geometry = window.QAZGEO_GEOMETRY;
  if (!runtime || !contracts || !geometry) throw new Error("QAZ map dependencies are unavailable");

  function setText(element, value) {
    if (element) element.textContent = value;
  }

  function setStatus(container, message, state) {
    var status = container.querySelector("[data-map-status]");
    setText(status, message);
    if (status) {
      status.dataset.avState = state;
      status.classList.toggle("av-badge--success", state === "ready");
      status.classList.toggle("av-badge--danger", state === "error");
      status.classList.toggle("av-badge--info", state !== "error" && state !== "ready");
    }
  }

  function fetchSnapshot() {
    if (!snapshotPromise) {
      snapshotPromise = runtime.fetchJsonAsset(DATA_PATH, {
        validate: contracts.validateRegionsGeoJson,
      }).then(function (payload) { return geometry.buildModel(payload, SOURCE_URL); });
    }
    return snapshotPromise;
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
    setStatus(container, "QazGeo · " + model.features.length + " реальных границ · проверенный срез", "ready");
    var source = container.querySelector("[data-map-source]");
    if (source) source.href = model.source || SOURCE_URL;
  }

  function renderError(container, error) {
    setStatus(container, "Срез QazGeo недоступен · карта скрыта", "error");
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
      setStatus(container, "Загружаем проверенный срез QazGeo…", "loading");
      fetchSnapshot().then(function (model) { renderMap(container, model); }).catch(function (error) { renderError(container, error); });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
}());
