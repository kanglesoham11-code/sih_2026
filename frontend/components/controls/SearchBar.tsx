'use client'

import { useState } from 'react'
import { Search, MapPin, Navigation } from 'lucide-react'
import { useStore } from '@/lib/store'
import { motion, AnimatePresence } from 'framer-motion'

interface SearchResult {
  name: string
  location: [number, number]
  type: string
}

// Indian coastal locations
const PRESET_LOCATIONS: SearchResult[] = [
  { name: 'Sassoon Dock & Jetty', location: [72.8333, 18.9067], type: 'port' },
  { name: 'Gateway of India', location: [72.8347, 18.9220], type: 'port' },
  { name: 'Bhaucha Dhakka / Ferry Wharf', location: [72.8505, 18.9560], type: 'port' },
  { name: 'Marine Drive Promenade', location: [72.8235, 18.9432], type: 'coast' },
  { name: 'Lotus Jetty & Worli Fort', location: [72.8167, 19.0000], type: 'coast' },
  { name: 'Bandra-Worli Sea Link Coastline', location: [72.8174, 19.0365], type: 'coast' },
  { name: 'Mahim Creek & Causeway', location: [72.8400, 19.0410], type: 'coast' },
  { name: 'Juhu Fishing Pier', location: [72.8267, 19.0988], type: 'coast' },
  { name: 'Bhati Dock (Madh Island)', location: [72.7929, 19.1508], type: 'coast' },
  { name: 'Arabian Sea', location: [68.0, 18.0], type: 'region' },
  { name: 'Bay of Bengal', location: [88.0, 15.0], type: 'region' },
]

export function SearchBar() {
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const { setMapViewState, setSelectedLocation } = useStore()

  const filteredLocations = query
    ? PRESET_LOCATIONS.filter((loc) =>
        loc.name.toLowerCase().includes(query.toLowerCase())
      )
    : PRESET_LOCATIONS

  const handleSelectLocation = (result: SearchResult) => {
    setMapViewState({
      longitude: result.location[0],
      latitude: result.location[1],
      zoom: result.type === 'city' ? 10 : 6,
    })
    setSelectedLocation(result.location)
    setQuery('')
    setIsOpen(false)
  }

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setIsOpen(true)
          }}
          onFocus={() => setIsOpen(true)}
          onBlur={() => setTimeout(() => setIsOpen(false), 200)}
          placeholder="Search locations..."
          className="w-full pl-10 pr-4 py-3 bg-white rounded-lg shadow-lg border border-gray-200
                   focus:outline-none focus:ring-2 focus:ring-ocean-500 text-sm"
        />
      </div>

      <AnimatePresence>
        {isOpen && filteredLocations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full mt-2 w-full bg-white rounded-lg shadow-xl border 
                     border-gray-200 overflow-hidden z-50 max-h-80 overflow-y-auto custom-scrollbar"
          >
            {filteredLocations.map((location, index) => (
              <button
                key={index}
                onClick={() => handleSelectLocation(location)}
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 
                         transition-colors text-left"
              >
                {location.type === 'port' ? (
                  <MapPin className="w-5 h-5 text-blue-600" />
                ) : location.type === 'coast' ? (
                  <Navigation className="w-5 h-5 text-teal-600" />
                ) : (
                  <Navigation className="w-5 h-5 text-gray-400" />
                )}
                <div>
                  <div className="font-medium text-sm">{location.name}</div>
                  <div className="text-xs text-gray-500">
                    {location.location[1].toFixed(4)}°N, {location.location[0].toFixed(4)}°E
                  </div>
                </div>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
