export const generateMockVessels = (count: number, centerLon: number, centerLat: number) => {
  return Array.from({ length: count }).map((_, i) => {
    // Generate vessels within a tiny 150m radius of the center (approx 0.0013 degrees)
    const radius = 0.0003 + Math.random() * 0.001
    const angle = Math.random() * Math.PI * 2
    return {
      id: `vessel-${i}`,
      lon: centerLon + Math.cos(angle) * radius,
      lat: centerLat + Math.sin(angle) * radius,
    }
  })
}

export const generateMockCatchData = (centerLon: number, centerLat: number) => {
  // A rough polygon for catch data heat strictly within the 200m radius
  const offset = 0.001
  return {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        properties: { intensity: 0.8 },
        geometry: {
          type: 'Polygon',
          coordinates: [[
            [centerLon - offset, centerLat - offset],
            [centerLon + offset, centerLat - offset],
            [centerLon + offset, centerLat + offset],
            [centerLon - offset, centerLat + offset],
            [centerLon - offset, centerLat - offset]
          ]]
        }
      },
      {
        type: 'Feature',
        properties: { intensity: 0.5 },
        geometry: {
          type: 'Polygon',
          coordinates: [[
            [centerLon - offset * 1.5, centerLat - offset * 0.5],
            [centerLon - offset, centerLat - offset * 0.5],
            [centerLon - offset, centerLat + offset],
            [centerLon - offset * 1.5, centerLat + offset],
            [centerLon - offset * 1.5, centerLat - offset * 0.5]
          ]]
        }
      }
    ]
  }
}

// Generate a valid GeoJSON circle polygon given radius in meters
export const generateRadiusPolygon = (centerLon: number, centerLat: number, radiusMeters: number) => {
  const points = 64;
  const coords = [];
  
  // 1 degree of latitude is approx 111,320 meters
  // 1 degree of longitude is approx 111,320 * cos(latitude) meters
  const latRatio = 111320;
  const lonRatio = 111320 * Math.cos(centerLat * (Math.PI / 180));
  
  const radiusLat = radiusMeters / latRatio;
  const radiusLon = radiusMeters / lonRatio;

  for (let i = 0; i < points; i++) {
    const angle = (i / points) * Math.PI * 2;
    coords.push([
      centerLon + Math.cos(angle) * radiusLon,
      centerLat + Math.sin(angle) * radiusLat
    ]);
  }
  // Ensure the polygon is perfectly closed by copying the exact first coordinate
  coords.push([...coords[0]]);

  return {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'Polygon',
          coordinates: [coords]
        }
      }
    ]
  }
}
