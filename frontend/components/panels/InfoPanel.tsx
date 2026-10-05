'use client'

import { useStore } from '@/lib/store'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  X, 
  MapPin, 
  Thermometer, 
  Waves, 
  Wind, 
  Fish,
  AlertTriangle,
  TrendingUp,
  Droplets,
} from 'lucide-react'
import { coordinateToString, formatTimestamp, getFreshnessColor, getFreshnessLabel } from '@/lib/utils'

export function InfoPanel() {
  const { selectedLocation, setSelectedLocation, portAnalysis } = useStore()

  const { data: observations, isLoading } = useQuery({
    queryKey: ['observations', selectedLocation],
    queryFn: () => {
      if (!selectedLocation) return null
      return apiClient.getObservations({
        lat: selectedLocation[1],
        lon: selectedLocation[0],
        radius_km: 50,
      })
    },
    enabled: !!selectedLocation,
  })

  const queryClient = useQueryClient()
  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', selectedLocation],
    queryFn: () => {
      if (!selectedLocation) return null
      return apiClient.getRecommendations({
        lat: selectedLocation[1],
        lon: selectedLocation[0],
      })
    },
    enabled: !!selectedLocation,
  })

  const handleRouteToPfz = () => {
    if (!selectedLocation) return
    const pfzZones = queryClient.getQueryData<any[]>(['pfz-zones'])
    if (pfzZones && pfzZones.length > 0) {
      // Find nearest PFZ center (naive distance calculation)
      let minDistance = Infinity
      let nearestPfzCenter: [number, number] | null = null

      pfzZones.forEach(zone => {
        // Simple bounding box center
        const coords = zone.geometry.coordinates[0]
        const sumLng = coords.reduce((sum: number, c: number[]) => sum + c[0], 0)
        const sumLat = coords.reduce((sum: number, c: number[]) => sum + c[1], 0)
        const centerLng = sumLng / coords.length
        const centerLat = sumLat / coords.length

        const dx = centerLng - selectedLocation[0]
        const dy = centerLat - selectedLocation[1]
        const dist = Math.sqrt(dx * dx + dy * dy)

        if (dist < minDistance) {
          minDistance = dist
          nearestPfzCenter = [centerLng, centerLat]
        }
      })

      if (nearestPfzCenter) {
        useStore.getState().setRouteToPfz({
          start: selectedLocation,
          end: nearestPfzCenter
        })
      }
    }
  }

  if (!selectedLocation) return null

  // Demo data for when backend is not connected
  const demoData = {
    sst: { value: '28.5°C', freshness: 'Fresh', color: 'text-blue-500' },
    chlorophyll: { value: '0.42 mg/m³', freshness: 'Recent', color: 'text-green-500' },
    waveHeight: { value: '1.2 m', freshness: 'Fresh', color: 'text-blue-500' },
    windSpeed: { value: '12 km/h NE', freshness: 'Live', color: 'text-green-500' },
    salinity: { value: '35.2 PSU', freshness: 'Recent', color: 'text-blue-500' },
  }

  // Process real observations if available
  let displayData = { ...demoData }
  if (observations && observations.length > 0) {
    const oceanData = observations.find((o: any) => o.type === 'ocean_params')?.parameters || {}
    const weatherData = observations.find((o: any) => o.type === 'weather')?.parameters || {}
    const waveData = observations.find((o: any) => o.type === 'wave_data')?.parameters || {}
    
    if (oceanData.sst !== undefined) {
      displayData.sst.value = `${oceanData.sst} ${oceanData.sst_unit || '°C'}`
    }
    if (oceanData.chlorophyll !== undefined) {
      displayData.chlorophyll.value = `${oceanData.chlorophyll} ${oceanData.chlorophyll_unit || 'mg/m³'}`
    }
    if (oceanData.salinity !== undefined) {
      displayData.salinity.value = `${oceanData.salinity} ${oceanData.salinity_unit || 'PSU'}`
    }
    if (waveData.wave_height !== undefined) {
      displayData.waveHeight.value = `${waveData.wave_height} ${waveData.wave_height_unit || 'm'}`
    }
    if (weatherData.wind_speed !== undefined) {
      displayData.windSpeed.value = `${weatherData.wind_speed} ${weatherData.wind_speed_unit || 'km/h'} ${weatherData.wind_direction_str || ''}`
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: -300 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -300 }}
        className="fixed left-4 top-1/2 -translate-y-1/2 w-80 bg-white rounded-lg 
                 shadow-2xl z-30 max-h-[70vh] flex flex-col overflow-hidden"
      >
        {/* Header */}
        <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-sky-50">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <MapPin className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-sm">Location Info</h3>
                <p className="text-xs text-gray-600 mt-1">
                  {coordinateToString(selectedLocation)}
                </p>
              </div>
            </div>
            <button
              onClick={() => setSelectedLocation(null)}
              className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="spinner"></div>
              <span className="ml-2 text-sm text-gray-600">Loading data...</span>
            </div>
          ) : (
            <>
              {/* Ocean Parameters */}
              <div>
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Waves className="w-4 h-4 text-blue-600" />
                  Ocean Parameters
                </h4>
                <div className="space-y-2">
                  <DataRow
                    icon={<Thermometer className="w-4 h-4" />}
                    label="Sea Surface Temp"
                    value={displayData.sst.value}
                    freshness={displayData.sst.freshness}
                    color={displayData.sst.color}
                  />
                  <DataRow
                    icon={<TrendingUp className="w-4 h-4" />}
                    label="Chlorophyll"
                    value={displayData.chlorophyll.value}
                    freshness={displayData.chlorophyll.freshness}
                    color={displayData.chlorophyll.color}
                  />
                  <DataRow
                    icon={<Droplets className="w-4 h-4" />}
                    label="Salinity"
                    value={displayData.salinity.value}
                    freshness={displayData.salinity.freshness}
                    color={displayData.salinity.color}
                  />
                </div>
              </div>

              {/* Weather */}
              <div>
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Wind className="w-4 h-4 text-sky-600" />
                  Weather Conditions
                </h4>
                <div className="space-y-2">
                  <DataRow
                    icon={<Waves className="w-4 h-4" />}
                    label="Wave Height"
                    value={displayData.waveHeight.value}
                    freshness={displayData.waveHeight.freshness}
                    color={displayData.waveHeight.color}
                  />
                  <DataRow
                    icon={<Wind className="w-4 h-4" />}
                    label="Wind Speed"
                    value={displayData.windSpeed.value}
                    freshness={displayData.windSpeed.freshness}
                    color={displayData.windSpeed.color}
                  />
                </div>
              </div>

              {/* Fishing Advisory / Port Analysis */}
              <div>
                <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Fish className="w-4 h-4 text-green-600" />
                  Fishing Advisory
                </h4>
                {portAnalysis ? (
                  <div className={`border rounded-lg p-3 ${
                    portAnalysis.risk_status?.includes('CRITICAL') ? 'bg-red-50 border-red-200 text-red-800' :
                    portAnalysis.risk_status?.includes('HIGH') ? 'bg-yellow-50 border-yellow-200 text-yellow-800' :
                    'bg-green-50 border-green-200 text-green-800'
                  }`}>
                    <div className="flex flex-col gap-3 text-sm">
                      <div className="font-bold border-b pb-2 border-black/10">
                        {portAnalysis.risk_status?.replace('_', ' ')}
                      </div>
                      <div className="text-xs">{portAnalysis.safety_advisory}</div>
                      
                      {portAnalysis.nearest_pfz && (
                        <>
                          <div className="flex items-center justify-between text-xs mt-2">
                            <span>Nearest PFZ Distance:</span>
                            <span className="font-semibold">{portAnalysis.pfz_distance_km} km</span>
                          </div>
                          <div className="flex items-center justify-between text-xs">
                            <span>Estimated Travel:</span>
                            <span className="font-semibold">{portAnalysis.estimated_travel_time_min} mins</span>
                          </div>
                          <button 
                            onClick={() => {
                              if (portAnalysis.map_actions) {
                                const routeAction = portAnalysis.map_actions.find((a: any) => a.type === 'route_to_pfz')
                                if (routeAction) {
                                  useStore.getState().setRouteToPfz({
                                    start: routeAction.start,
                                    end: routeAction.end
                                  })
                                }
                              }
                            }}
                            className="bg-red-600 hover:bg-red-700 text-white py-2 px-3 mt-2 rounded-md text-xs font-semibold flex items-center justify-center gap-2 transition-all active:scale-95 shadow-[0_0_15px_rgba(220,38,38,0.5)]"
                          >
                            <MapPin className="w-3 h-3" />
                            Navigate to Safest PFZ
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="text-sm text-green-800">
                      {recommendations ? (
                        <div className="flex flex-col gap-3">
                          <div>{recommendations.summary}</div>
                          <button 
                            onClick={handleRouteToPfz}
                            className="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-md text-xs font-semibold flex items-center justify-center gap-2 transition-all active:scale-95"
                          >
                            <MapPin className="w-3 h-3" />
                            Navigate to Nearest PFZ
                          </button>
                        </div>
                      ) : (
                        <>
                          <div className="font-medium mb-1">Good fishing conditions</div>
                          <div className="text-xs">
                            Moderate chlorophyll levels detected. Expected species: Tuna, Mackerel.
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>


            </>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}

function DataRow({ 
  icon, 
  label, 
  value, 
  freshness, 
  color 
}: { 
  icon: React.ReactNode
  label: string
  value: string
  freshness: string
  color: string
}) {
  return (
    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-2">
        <div className={`${color}`}>{icon}</div>
        <span className="text-xs text-gray-700">{label}</span>
      </div>
      <div className="text-right">
        <div className="text-sm font-medium">{value}</div>
        <div className={`text-xs ${color}`}>{freshness}</div>
      </div>
    </div>
  )
}
