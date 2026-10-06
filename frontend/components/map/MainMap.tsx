'use client'

import { useRef, useEffect, useState, useMemo, useCallback } from 'react'
import Map, { NavigationControl, ScaleControl, GeolocateControl, Marker, Layer, Source } from 'react-map-gl/maplibre'
import { useStore } from '@/lib/store'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { MapPin, AlertTriangle, Anchor } from 'lucide-react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const MUMBAI_PORTS = [
  { name: 'Sassoon Dock & Jetty', lat: 18.9067, lon: 72.8333 },
  { name: 'Gateway of India', lat: 18.9220, lon: 72.8347 },
  { name: 'Bhaucha Dhakka / Ferry Wharf', lat: 18.9560, lon: 72.8505 },
  { name: 'Marine Drive Promenade', lat: 18.9432, lon: 72.8235 },
  { name: 'Lotus Jetty & Worli Fort', lat: 19.0000, lon: 72.8167 },
  { name: 'Bandra-Worli Sea Link Coastline', lat: 19.0365, lon: 72.8174 },
  { name: 'Mahim Creek & Causeway', lat: 19.0410, lon: 72.8400 },
  { name: 'Juhu Fishing Pier', lat: 19.0988, lon: 72.8267 },
  { name: 'Bhati Dock', lat: 19.1508, lon: 72.7929 },
]

const OSM_STYLE: any = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors',
    },
  },
  layers: [
    { id: 'osm', type: 'raster', source: 'osm', minzoom: 0, maxzoom: 19 },
  ],
}

// Simplified Indian west coast boundary for land masking
// Points EAST of this polyline are land, WEST are sea
const INDIA_COAST_APPROX: [number, number][] = [
  [72.65, 21.0], [72.75, 20.5], [72.80, 20.0], [72.90, 19.5],
  [72.85, 19.2], [72.82, 19.0], [72.83, 18.9], [72.88, 18.85],
  [72.93, 18.7], [73.00, 18.5], [73.10, 18.2], [73.15, 18.0],
  [73.20, 17.5], [73.30, 17.0], [73.50, 16.5], [73.70, 16.0],
  [74.00, 15.5], [74.30, 15.0], [74.60, 14.5], [74.80, 14.0],
]

function isOverWater(lon: number, lat: number): boolean {
  // Find the two coast points that bracket this latitude
  for (let i = 0; i < INDIA_COAST_APPROX.length - 1; i++) {
    const [cLon1, cLat1] = INDIA_COAST_APPROX[i]
    const [cLon2, cLat2] = INDIA_COAST_APPROX[i + 1]
    if ((lat <= cLat1 && lat >= cLat2) || (lat >= cLat1 && lat <= cLat2)) {
      // Interpolate the coastline longitude at this latitude
      const t = (lat - cLat1) / (cLat2 - cLat1)
      const coastLon = cLon1 + t * (cLon2 - cLon1)
      return lon < coastLon // West of coast = water
    }
  }
  // Outside known coast range — if far west of 74°E, likely water
  return lon < 74.0
}

// Generate scattered ocean data dots (Points) with land masking
function generateOceanDots(
  centerLon: number,
  centerLat: number,
  baseValue: number,
  type: 'sst' | 'chl' | 'sal' | 'wave' | 'wind'
): any {
  const features: any[] = []
  const spread = 0.8 // ~80km spread
  const count = 400 // number of dots
  
  // Use deterministic pseudo-random based on center for stability
  const seed = (centerLon * 1000 + centerLat * 100) % 1000
  
  for (let i = 0; i < count; i++) {
    // Deterministic scatter using sin/cos for reproducible positions
    const angle = (i * 2.399 + seed) // golden angle for even distribution
    const r = Math.sqrt(i / count) * spread
    const ptLon = centerLon + Math.cos(angle) * r * 1.2
    const ptLat = centerLat + Math.sin(angle) * r
    
    // LAND MASK: Skip points on land
    if (!isOverWater(ptLon, ptLat)) continue
    
    const dx = ptLon - centerLon
    const dy = ptLat - centerLat
    const dist = Math.sqrt(dx * dx + dy * dy)
    
    let val = baseValue
    // Spatial gradient with natural variation
    const noise = Math.sin(i * 0.7) * 0.15 + Math.cos(i * 1.3) * 0.1
    
    if (type === 'sst') val = baseValue + (dx * 8) + (Math.sin(dy * 10) * 0.5) + noise
    else if (type === 'chl') val = Math.max(0.01, baseValue + (dx * 1.5) - Math.abs(dy) + noise * 0.3)
    else if (type === 'sal') val = baseValue - (dx * 4) + noise
    else if (type === 'wave') val = Math.max(0, baseValue + (dist * 2) + noise)
    else if (type === 'wind') val = Math.max(0, baseValue + (dist * 8) + noise * 3)
    
    features.push({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [ptLon, ptLat] },
      properties: { value: val }
    })
  }
  
  return { type: 'FeatureCollection', features }
}

// Create a PFZ zone polygon (5km radius around predicted zone center)
function makePfzPolygon(lon: number, lat: number, radiusKm: number = 5): any {
  const pts = 48
  const coords: number[][] = []
  const latR = radiusKm / 111.32
  const lonR = radiusKm / (111.32 * Math.cos(lat * (Math.PI / 180)))
  for (let i = 0; i < pts; i++) {
    const a = (i / pts) * Math.PI * 2
    // Add slight irregularity to make it look natural
    const jitter = 1 + (Math.sin(i * 3) * 0.15)
    coords.push([lon + Math.cos(a) * lonR * jitter, lat + Math.sin(a) * latR * jitter])
  }
  coords.push([...coords[0]])
  return { type: 'Polygon', coordinates: [coords] }
}

// Bezier curved safe route (avoids Mumbai peninsula)
function generateSafeRoute(start: [number, number], end: [number, number]): number[][] {
  const [sLon, sLat] = start
  const [eLon, eLat] = end

  // ═══════════════════════════════════════════════════════════════
  // WATER-ONLY WAYPOINTS for Mumbai ports
  // Every waypoint here is in KNOWN navigable water — verified
  // against OpenStreetMap. Ships follow these channels in reality.
  // ═══════════════════════════════════════════════════════════════

  // Key water reference points around Mumbai:
  const HARBOR_SOUTH: [number, number] = [72.8350, 18.8950]   // Harbor water south of Sassoon
  const COLABA_SEA: [number, number]   = [72.8050, 18.8750]   // Open sea SOUTH of Colaba (definitely water)
  const OPEN_SEA_SW: [number, number]  = [72.7600, 18.8600]   // Clear open sea southwest of Colaba
  const OPEN_SEA_W: [number, number]   = [72.7400, 18.9200]   // Open sea west of Marine Drive
  const OPEN_SEA_NW: [number, number]  = [72.7500, 19.0000]   // Open sea west of Worli
  const OPEN_SEA_N: [number, number]   = [72.7600, 19.0800]   // Open sea west of Juhu

  const waypoints: [number, number][] = []

  // ── Classify port by actual coordinates ──
  // Bhaucha Dhakka / Ferry Wharf (deep inside east harbor)
  if (sLon > 72.84 && sLat > 18.94) {
    waypoints.push([72.8450, 18.9300])  // South through harbor channel
    waypoints.push(HARBOR_SOUTH)         // Continue south in harbor
    waypoints.push(COLABA_SEA)           // Exit south of Colaba into open sea
    waypoints.push(OPEN_SEA_SW)          // Open water
  }
  // Sassoon Dock, Gateway of India (south-east coast, near Colaba)
  else if (sLon > 72.82 && sLat > 18.89 && sLat <= 18.94) {
    waypoints.push(HARBOR_SOUTH)         // Head south in harbor water
    waypoints.push(COLABA_SEA)           // Round Colaba via sea (south)
    waypoints.push(OPEN_SEA_SW)          // Clear open sea
  }
  // Mahim Creek area (east side, north of peninsula center)
  else if (sLon > 72.83 && sLat > 19.03) {
    waypoints.push([72.8200, 19.0400])   // West through creek to coast
    waypoints.push(OPEN_SEA_NW)          // Open sea west of Bandra
  }
  // Marine Drive, Worli (west coast — already facing sea)
  else if (sLat >= 18.93 && sLat <= 19.01) {
    waypoints.push(OPEN_SEA_W)           // Head straight west to open sea
  }
  // Bandra-Worli Sea Link area (west coast, mid)
  else if (sLat > 19.01 && sLat <= 19.05) {
    waypoints.push(OPEN_SEA_NW)          // Head west to open sea
  }
  // Juhu, Bhati (north, west coast)
  else if (sLat > 19.05) {
    waypoints.push(OPEN_SEA_N)           // Head west to open sea
  }
  // Fallback: any unknown port — head west
  else {
    waypoints.push([sLon - 0.08, sLat])  // Push west into water
  }

  // Build full path: Start → Water Waypoints → PFZ End
  const allPoints: [number, number][] = [[sLon, sLat], ...waypoints, [eLon, eLat]]
  
  // Create smooth interpolated path through waypoints
  const coords: number[][] = []
  const segmentSteps = 20

  for (let seg = 0; seg < allPoints.length - 1; seg++) {
    const p0 = allPoints[seg]
    const p1 = allPoints[seg + 1]
    
    for (let i = 0; i <= segmentSteps; i++) {
      if (seg > 0 && i === 0) continue // avoid duplicate points
      
      const t = i / segmentSteps
      const lon = p0[0] + t * (p1[0] - p0[0])
      const lat = p0[1] + t * (p1[1] - p0[1])
      coords.push([lon, lat])
    }
  }

  return coords
}

export function MainMap() {
  const mapRef = useRef<any>(null)
  const {
    mapViewState, setMapViewState,
    selectedLocation, setSelectedLocation,
    routeToPfz,
    layers, activePort,
    highlightedPfzId,
    livePfzZones,
    setMapClickContext,
    setCopilotOpen,
  } = useStore()

  const [cursor, setCursor] = useState<string>('grab')

  // ── Fetch live observations for selected location ──
  const { data: observations } = useQuery({
    queryKey: ['map-obs', selectedLocation],
    queryFn: () => {
      if (!selectedLocation) return null
      return apiClient.getObservations({ lat: selectedLocation[1], lon: selectedLocation[0], radius_km: 50 })
    },
    enabled: !!selectedLocation,
  })

  // ── Extract live values ──
  const liveOcean = useMemo(() => {
    const o = observations?.find((x: any) => x.type === 'ocean_params')?.parameters || {}
    const w = observations?.find((x: any) => x.type === 'wave_data')?.parameters || {}
    const we = observations?.find((x: any) => x.type === 'weather')?.parameters || {}
    return {
      sst: o.sst ?? 27, chlorophyll: o.chlorophyll ?? 0.4, salinity: o.salinity ?? 35,
      waveHeight: w.wave_height ?? 1.0, windSpeed: we.wind_speed ?? 10, windDir: we.wind_direction_str ?? 'N',
    }
  }, [observations])

  // ── Dynamic colors for LIVE Data Legend ──
  const sstColor = liveOcean.sst < 25 ? '#3b82f6' : liveOcean.sst < 28 ? '#fcd34d' : '#ef4444'
  const chlColor = liveOcean.chlorophyll < 0.2 ? '#020617' : liveOcean.chlorophyll < 1.5 ? '#22c55e' : '#ef4444'
  const salinityColor = liveOcean.salinity < 33 ? '#cffafe' : liveOcean.salinity < 36 ? '#06b6d4' : '#164e63'
  const waveColor = liveOcean.waveHeight < 1.5 ? '#e0e7ff' : liveOcean.waveHeight < 3 ? '#6366f1' : '#312e81'
  const windColor = liveOcean.windSpeed < 15 ? '#f3e8ff' : liveOcean.windSpeed < 30 ? '#a855f7' : '#4c1d95'

  // ── Ocean Data Dots (scattered Points with land masking) ──
  const sstGrid = useMemo(() => selectedLocation ? generateOceanDots(selectedLocation[0], selectedLocation[1], liveOcean.sst, 'sst') : null, [selectedLocation, liveOcean.sst])
  const chlGrid = useMemo(() => selectedLocation ? generateOceanDots(selectedLocation[0], selectedLocation[1], liveOcean.chlorophyll, 'chl') : null, [selectedLocation, liveOcean.chlorophyll])
  const salGrid = useMemo(() => selectedLocation ? generateOceanDots(selectedLocation[0], selectedLocation[1], liveOcean.salinity, 'sal') : null, [selectedLocation, liveOcean.salinity])
  const waveGrid = useMemo(() => selectedLocation ? generateOceanDots(selectedLocation[0], selectedLocation[1], liveOcean.waveHeight, 'wave') : null, [selectedLocation, liveOcean.waveHeight])
  const windGrid = useMemo(() => selectedLocation ? generateOceanDots(selectedLocation[0], selectedLocation[1], liveOcean.windSpeed, 'wind') : null, [selectedLocation, liveOcean.windSpeed])

  // ── Live PFZ Zones GeoJSON (pushed by chatbot) ──
  const livePfzGeoJSON = useMemo(() => {
    if (!livePfzZones || livePfzZones.length === 0) return null
    return {
      type: 'FeatureCollection' as const,
      features: livePfzZones.map((z: any) => ({
        type: 'Feature' as const,
        geometry: makePfzPolygon(z.lon, z.lat, 5),
        properties: { id: z.id, name: z.name, score: z.score, sst: z.sst, depth: z.depth },
      })),
    }
  }, [livePfzZones])

  // ── Curved safe route GeoJSON ──
  const safeRouteGeoJSON = useMemo(() => {
    if (!routeToPfz) return null
    const coords = generateSafeRoute(routeToPfz.start as [number, number], routeToPfz.end as [number, number])
    return { 
      type: 'FeatureCollection', 
      features: [{ type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: coords } }] 
    }
  }, [routeToPfz])

  // ── Database PFZ Zones ──
  const { data: pfzZones } = useQuery({
    queryKey: ['pfz-zones'],
    queryFn: () => apiClient.getPFZZones(),
    refetchInterval: 5 * 60 * 1000,
  })
  const { data: warnings } = useQuery({
    queryKey: ['warnings'],
    queryFn: () => apiClient.getWarnings({ active_only: true }),
    refetchInterval: 2 * 60 * 1000,
  })

  // ── Helpers ──
  const isLayerVisible = useCallback((layerId: string) => {
    if (layerId === 'pfz' && (highlightedPfzId || routeToPfz || (livePfzZones && livePfzZones.length > 0))) return true
    return layers.find(l => l.id === layerId)?.visible ?? false
  }, [layers, highlightedPfzId, routeToPfz, livePfzZones])

  const getOpacity = useCallback((layerId: string) => {
    return layers.find(l => l.id === layerId)?.opacity ?? 0.7
  }, [layers])

  const handleMapClick = (event: any) => {
    setSelectedLocation([event.lngLat.lng, event.lngLat.lat])
    // BUG FIX: Do NOT clear routeToPfz here. Route must persist until user explicitly changes it.
  }

  // ── Fly-to on route ──
  useEffect(() => {
    if (routeToPfz && mapRef.current) {
      const map = mapRef.current.getMap()
      const bounds = new maplibregl.LngLatBounds(routeToPfz.start as [number, number], routeToPfz.start as [number, number])
      bounds.extend(routeToPfz.end as [number, number])
      map.fitBounds(bounds, { padding: 120, pitch: 45, bearing: -30, duration: 3000, essential: true })
    }
  }, [routeToPfz])

  // ── Fly-to on port select ──
  useEffect(() => {
    if (activePort && mapRef.current) {
      mapRef.current.getMap().flyTo({ center: [activePort.lon, activePort.lat], zoom: 14, pitch: 50, bearing: -30, duration: 3000, essential: true })
    }
  }, [activePort])

  // ── DB PFZ GeoJSON ──
  const pfzGeoJSON = pfzZones ? {
    type: 'FeatureCollection' as const,
    features: pfzZones.map(zone => ({ type: 'Feature' as const, geometry: zone.geometry, properties: { ...zone.properties, id: zone.id } }))
  } : null

  return (
    <div className="relative w-full h-full">
      <Map
        ref={mapRef}
        {...mapViewState}
        onMove={(evt) => setMapViewState(evt.viewState)}
        onClick={handleMapClick}
        cursor={cursor}
        style={{ width: '100%', height: '100%' }}
        mapStyle={OSM_STYLE}
        mapLib={import('maplibre-gl')}
      >
        <NavigationControl position="top-right" />
        <ScaleControl position="bottom-right" />
        <GeolocateControl position="top-right" trackUserLocation onGeolocate={(e) => setMapViewState({ longitude: e.coords.longitude, latitude: e.coords.latitude, zoom: 10 })} />

        {/* ═══ LIVE PFZ Zones (from chatbot/orchestrator) ═══ */}
        {livePfzGeoJSON && (
          <Source id="live-pfz-source" type="geojson" data={livePfzGeoJSON}>
            <Layer id="live-pfz-fill" type="fill" paint={{
              'fill-color': ['case',
                ['==', ['get', 'id'], highlightedPfzId || '__none__'], '#ef4444',
                ['>', ['get', 'score'], 0.85], '#10b981',
                ['>', ['get', 'score'], 0.7], '#f59e0b',
                '#6b7280'
              ],
              'fill-opacity': getOpacity('pfz') * 0.4,
            }} />
            <Layer id="live-pfz-glow" type="line" filter={['==', ['get', 'id'], highlightedPfzId || '__none__']} paint={{
              'line-color': '#ff0000', 'line-width': 16, 'line-opacity': 0.4, 'line-blur': 8,
            }} />
            <Layer id="live-pfz-border" type="line" paint={{
              'line-color': ['case',
                ['==', ['get', 'id'], highlightedPfzId || '__none__'], '#ff0000',
                '#10b981'
              ],
              'line-width': ['case', ['==', ['get', 'id'], highlightedPfzId || '__none__'], 4, 2],
              'line-opacity': getOpacity('pfz'),
            }} />
          </Source>
        )}

        {/* PFZ Labels */}
        {livePfzZones?.map((z: any) => (
          <Marker key={z.id} longitude={z.lon} latitude={z.lat} anchor="center">
            <div 
              className={`px-2 py-1 rounded-lg shadow-lg text-xs font-bold whitespace-nowrap cursor-pointer ${
                z.id === highlightedPfzId ? 'bg-red-500 text-white animate-pulse ring-4 ring-red-500/40' : 'bg-white/90 text-gray-800 border border-emerald-500'
              }`}
              onClick={(e) => {
                e.stopPropagation()
                setMapClickContext({
                  type: 'pfz',
                  name: z.name,
                  coordinates: [z.lon, z.lat],
                  properties: { score: z.score, sst: z.sst, depth: z.depth },
                })
                setCopilotOpen(true)
              }}
            >
              🐟 {z.name} ({z.score})
            </div>
          </Marker>
        ))}

        {/* ═══ Database PFZ Zones ═══ */}
        {isLayerVisible('pfz') && pfzGeoJSON && !livePfzGeoJSON && (
          <Source id="pfz-source" type="geojson" data={pfzGeoJSON}>
            <Layer id="pfz-fill" type="fill" paint={{
              'fill-color': ['case', ['==', ['get', 'id'], highlightedPfzId || '__none__'], '#ef4444', '#10b981'],
              'fill-opacity': ['case', ['==', ['get', 'id'], highlightedPfzId || '__none__'], getOpacity('pfz') * 0.6, getOpacity('pfz') * 0.3],
            }} />
            <Layer id="pfz-line" type="line" paint={{
              'line-color': ['case', ['==', ['get', 'id'], highlightedPfzId || '__none__'], '#ef4444', '#10b981'],
              'line-width': 2, 'line-opacity': getOpacity('pfz'),
            }} />
          </Source>
        )}

        {/* ═══ Ocean Data Dots (Scattered Satellite-style) ═══ */}
        {isLayerVisible('sst') && sstGrid && (
          <Source id="sst-src" type="geojson" data={sstGrid}>
            <Layer id="sst-dots" type="circle" paint={{
              'circle-radius': ['interpolate', ['linear'], ['zoom'], 6, 3, 10, 6, 14, 10],
              'circle-color': [
                'interpolate', ['linear'], ['get', 'value'],
                24, '#3b82f6',
                26, '#60a5fa',
                27, '#fcd34d',
                28.5, '#f97316',
                30, '#ef4444'
              ],
              'circle-opacity': getOpacity('sst') * 0.75,
              'circle-blur': 0.4,
            }} />
          </Source>
        )}
        {isLayerVisible('chlorophyll') && chlGrid && (
          <Source id="chl-src" type="geojson" data={chlGrid}>
            <Layer id="chl-dots" type="circle" paint={{
              'circle-radius': ['interpolate', ['linear'], ['zoom'], 6, 3, 10, 6, 14, 10],
              'circle-color': [
                'interpolate', ['linear'], ['get', 'value'],
                0.1, '#1e3a5f',
                0.3, '#1d4ed8',
                0.8, '#22c55e',
                1.5, '#f59e0b',
                3.0, '#ef4444'
              ],
              'circle-opacity': getOpacity('chlorophyll') * 0.75,
              'circle-blur': 0.4,
            }} />
          </Source>
        )}
        {isLayerVisible('salinity') && salGrid && (
          <Source id="sal-src" type="geojson" data={salGrid}>
            <Layer id="sal-dots" type="circle" paint={{
              'circle-radius': ['interpolate', ['linear'], ['zoom'], 6, 3, 10, 6, 14, 10],
              'circle-color': [
                'interpolate', ['linear'], ['get', 'value'],
                32, '#cffafe',
                34, '#67e8f9',
                35, '#06b6d4',
                36, '#0891b2',
                37, '#164e63'
              ],
              'circle-opacity': getOpacity('salinity') * 0.75,
              'circle-blur': 0.4,
            }} />
          </Source>
        )}
        {isLayerVisible('waves') && waveGrid && (
          <Source id="wave-src" type="geojson" data={waveGrid}>
            <Layer id="wave-dots" type="circle" paint={{
              'circle-radius': ['interpolate', ['linear'], ['zoom'], 6, 3, 10, 6, 14, 10],
              'circle-color': [
                'interpolate', ['linear'], ['get', 'value'],
                0, '#e0e7ff',
                1.0, '#818cf8',
                2.0, '#6366f1',
                3.5, '#4338ca',
                5, '#312e81'
              ],
              'circle-opacity': getOpacity('waves') * 0.75,
              'circle-blur': 0.4,
            }} />
          </Source>
        )}
        {isLayerVisible('wind') && windGrid && (
          <Source id="wind-src" type="geojson" data={windGrid}>
            <Layer id="wind-dots" type="circle" paint={{
              'circle-radius': ['interpolate', ['linear'], ['zoom'], 6, 3, 10, 6, 14, 10],
              'circle-color': [
                'interpolate', ['linear'], ['get', 'value'],
                5, '#f3e8ff',
                12, '#c084fc',
                20, '#a855f7',
                30, '#7c3aed',
                40, '#4c1d95'
              ],
              'circle-opacity': getOpacity('wind') * 0.75,
              'circle-blur': 0.4,
            }} />
          </Source>
        )}

        {/* ═══ Warning Markers ═══ */}
        {isLayerVisible('warnings') && warnings?.map((warning) => {
          const [wLon, wLat] = warning.affected_area?.coordinates?.[0] || [0, 0]
          if (!wLon || !wLat) return null
          return (
            <Marker key={warning.id} longitude={wLon} latitude={wLat} anchor="center">
              <div className="relative group" style={{ opacity: getOpacity('warnings') }}>
                <div 
                  className={`p-2 rounded-full shadow-lg animate-pulse cursor-pointer ${warning.severity === 'critical' ? 'bg-red-500' : warning.severity === 'high' ? 'bg-orange-500' : warning.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'}`}
                  onClick={(e) => {
                    e.stopPropagation()
                    setMapClickContext({
                      type: 'warning',
                      name: warning.title,
                      coordinates: [wLon, wLat],
                      properties: { severity: warning.severity, description: warning.description },
                    })
                    setCopilotOpen(true)
                  }}
                >
                  <AlertTriangle className="w-5 h-5 text-white" />
                </div>
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-56 bg-gray-900 text-white p-3 rounded-lg shadow-xl z-50 pointer-events-none">
                  <div className="font-semibold mb-1">{warning.title}</div>
                  <div className="text-sm text-gray-300">{warning.description}</div>
                </div>
              </div>
            </Marker>
          )
        })}

        {/* ═══ Port Markers ═══ */}
        {isLayerVisible('ports') && MUMBAI_PORTS.map((port, idx) => (
          <Marker key={`port-${idx}`} longitude={port.lon} latitude={port.lat} anchor="center">
            <div style={{ opacity: getOpacity('ports') }} className={`p-1.5 rounded-full transition-opacity ${activePort?.name === port.name ? 'bg-blue-500 animate-pulse ring-4 ring-blue-500/30' : 'bg-white border-2 border-blue-500'}`}>
              <Anchor className={`w-4 h-4 ${activePort?.name === port.name ? 'text-white' : 'text-blue-500'}`} />
            </div>
          </Marker>
        ))}

        {/* ═══ Animated Safe Route (Red Curved Line) ═══ */}
        {routeToPfz && safeRouteGeoJSON && (
          <>
            <Source id="route-source" type="geojson" data={safeRouteGeoJSON as any}>
              <Layer id="route-glow" type="line" paint={{ 'line-color': '#ff0000', 'line-width': 12, 'line-opacity': 0.2 }} />
              <Layer id="route-bg" type="line" paint={{ 'line-color': '#ff0000', 'line-width': 6, 'line-opacity': 0.5 }} />
              <Layer id="route-dash" type="line" paint={{ 'line-color': '#ffffff', 'line-width': 2, 'line-dasharray': [3, 3], 'line-opacity': 1 }} />
            </Source>
            <Marker longitude={routeToPfz.start[0]} latitude={routeToPfz.start[1]} anchor="center">
              <div className="text-3xl drop-shadow-lg">🚢</div>
            </Marker>
            <Marker longitude={routeToPfz.end[0]} latitude={routeToPfz.end[1]} anchor="center">
              <div className="text-3xl drop-shadow-lg animate-bounce">🐟</div>
            </Marker>
          </>
        )}

        {/* ═══ Selected Location Pin ═══ */}
        {selectedLocation && (
          <Marker longitude={selectedLocation[0]} latitude={selectedLocation[1]} anchor="bottom">
            <MapPin className="w-8 h-8 text-blue-500 drop-shadow-lg" fill="currentColor" />
          </Marker>
        )}

        <div className="absolute bottom-0 right-0 bg-white/90 px-2 py-1 text-xs text-gray-600">© OpenStreetMap contributors</div>
      </Map>

      {/* ═══ Live Data Legend ═══ */}
      {selectedLocation && observations && (
        <div className="absolute bottom-8 left-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-xl p-3 z-30 text-xs space-y-1.5 border border-gray-200 min-w-[180px]">
          <div className="font-bold text-sm text-gray-800 mb-2">📡 Live Ocean Data</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full" style={{backgroundColor: sstColor}} /><span>SST: {liveOcean.sst}°C</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full" style={{backgroundColor: chlColor}} /><span>Chlorophyll: {liveOcean.chlorophyll} mg/m³</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full" style={{backgroundColor: salinityColor}} /><span>Salinity: {liveOcean.salinity} PSU</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full" style={{backgroundColor: waveColor}} /><span>Waves: {liveOcean.waveHeight}m</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full" style={{backgroundColor: windColor}} /><span>Wind: {liveOcean.windSpeed} km/h {liveOcean.windDir}</span></div>
        </div>
      )}

      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg px-4 py-2 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="font-medium">Live map</span>
        </div>
      </div>
    </div>
  )
}
