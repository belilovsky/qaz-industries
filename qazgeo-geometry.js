(function (root, factory) {
  'use strict';

  const geometry = Object.freeze(factory());
  if (typeof module === 'object' && module.exports) module.exports = geometry;
  if (root) root.QAZGEO_GEOMETRY = geometry;
}(typeof globalThis === 'undefined' ? this : globalThis, function () {
  'use strict';

  function collectPoints(node, output) {
    if (!Array.isArray(node)) return output;
    if (node.length >= 2 && typeof node[0] === 'number' && typeof node[1] === 'number') {
      output.push([node[0], node[1]]);
      return output;
    }
    node.forEach((child) => collectPoints(child, output));
    return output;
  }

  function projectPoint(point, bounds) {
    return [
      (point[0] - bounds.minX) * bounds.scale + bounds.offsetX,
      (bounds.maxY - point[1]) * bounds.scale + bounds.offsetY,
    ];
  }

  function pathForRing(ring, bounds) {
    if (!Array.isArray(ring) || ring.length < 3) return '';
    const first = projectPoint(ring[0], bounds);
    let path = `M ${first[0].toFixed(2)} ${first[1].toFixed(2)}`;
    for (let index = 1; index < ring.length; index += 1) {
      const point = projectPoint(ring[index], bounds);
      path += ` L ${point[0].toFixed(2)} ${point[1].toFixed(2)}`;
    }
    return `${path} Z`;
  }

  function pathForGeometry(geometry, bounds) {
    if (geometry.type === 'Polygon') {
      return geometry.coordinates.map((ring) => pathForRing(ring, bounds)).join(' ');
    }
    if (geometry.type === 'MultiPolygon') {
      return geometry.coordinates.map((polygon) => (
        polygon.map((ring) => pathForRing(ring, bounds)).join(' ')
      )).join(' ');
    }
    throw new Error(`Unsupported QazGeo geometry: ${geometry.type}`);
  }

  function projectionBounds(features, width = 1000, height = 560, padding = 30) {
    const points = [];
    features.forEach((feature) => collectPoints(feature.geometry.coordinates, points));
    if (!points.length) throw new Error('QazGeo snapshot has no coordinates');
    const xs = points.map((point) => point[0]);
    const ys = points.map((point) => point[1]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const scale = Math.min(
      (width - padding * 2) / Math.max(maxX - minX, 0.1),
      (height - padding * 2) / Math.max(maxY - minY, 0.1),
    );
    return {
      minX,
      maxY,
      scale,
      offsetX: (width - (maxX - minX) * scale) / 2,
      offsetY: (height - (maxY - minY) * scale) / 2,
    };
  }

  function buildModel(payload, fallbackSource) {
    const bounds = projectionBounds(payload.features);
    return {
      source: payload.source || fallbackSource,
      features: payload.features.map((feature) => {
        const properties = feature.properties;
        return {
          id: String(properties.code),
          name: String(properties.name_ru || properties.code),
          nameEn: String(properties.name_en || properties.code),
          type: String(properties.region_type || 'region'),
          path: pathForGeometry(feature.geometry, bounds),
        };
      }),
    };
  }

  return { buildModel, collectPoints, pathForGeometry, projectionBounds };
}));
