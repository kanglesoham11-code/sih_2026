'use client'

import { useStore } from '@/lib/store'
import { motion } from 'framer-motion'
import { Anchor, Ship, Fish, Waves, MapPin } from 'lucide-react'
import { useState } from 'react'

const OFFSHORE_HUBS = [
  {
    name: 'Sassoon Dock & Jetty',
    region: 'Colaba',
    lat: 18.9067,
    lon: 72.8333,
    category: 'Offshore',
    description: 'Major historic fishing dock in South Mumbai. Gateway to deep sea grounds.',
    species: ['groupers', 'snappers', 'croakers']
  },
  {
    name: 'Gateway of India',
    region: 'Colaba',
    lat: 18.9220,
    lon: 72.8347,
    category: 'Offshore',
    description: 'Starting point for chartered deep sea fishing excursions.',
    species: ['Barramundi', 'Giant Trevally']
  },
  {
    name: 'Bhaucha Dhakka / Ferry Wharf',
    region: 'Mazgaon',
    lat: 18.9560,
    lon: 72.8505,
    category: 'Offshore',
    description: 'Commercial fishing hub. Good access to Elephanta island grounds.',
    species: ['bottom fishing near Elephanta']
  }
]

const COASTAL_SPOTS = [
  {
    name: 'Marine Drive Promenade',
    region: 'Girgaon',
    lat: 18.9432,
    lon: 72.8235,
    category: 'Coastal',
    description: 'Iconic promenade fishing, especially during monsoons.',
    species: ['mullet', 'ribbonfish']
  },
  {
    name: 'Lotus Jetty & Worli Fort',
    region: 'Worli',
    lat: 19.0000,
    lon: 72.8167,
    category: 'Coastal',
    description: 'Rocky outcrops offering excellent shore casting opportunities.',
    species: ['rockfish', 'pomfret']
  },
  {
    name: 'Bandra-Worli Sea Link Coastline',
    region: 'Bandra',
    lat: 19.0365,
    lon: 72.8174,
    category: 'Coastal',
    description: 'Productive coastal stretches around the pillars.',
    species: ['mackerel', 'kingfish']
  },
  {
    name: 'Mahim Creek & Causeway',
    region: 'Mahim',
    lat: 19.0410,
    lon: 72.8400,
    category: 'Coastal',
    description: 'Estuary environment drawing specific creek species.',
    species: ['Indian mackerel', 'catfish']
  },
  {
    name: 'Juhu Fishing Pier',
    region: 'Juhu',
    lat: 19.0988,
    lon: 72.8267,
    category: 'Coastal',
    description: 'Classic surf fishing spot along the sandy beach.',
    species: ['surf fishing']
  },
  {
    name: 'Bhati Dock',
    region: 'Madh Island',
    lat: 19.1508,
    lon: 72.7929,
    category: 'Coastal',
    description: 'Traditional Koli fishing village with rich coastal biodiversity.',
    species: ['prawns', 'coastal species']
  }
]

export function FishingHubSelector() {
  const { setActivePort, setShowFishingHub, setSelectedLocation, setMapViewState, setPortAnalysis,
    setRouteToPfz, setHighlightedPfzId, setLivePfzZones, addChatMessage, setSessionId, setCopilotOpen } = useStore()
  const [loading, setLoading] = useState(false)

  const handleSelectPort = async (port: any) => {
    setLoading(true)
    setActivePort(port)
    setSelectedLocation([port.lon, port.lat])
    setMapViewState({
      longitude: port.lon,
      latitude: port.lat,
      zoom: 14,
      pitch: 50,
      bearing: -30
    })
    
    // 1. Fetch port analysis (optional, may fail)
    try {
      const res = await fetch(`http://localhost:8000/api/port-analysis?lat=${port.lat}&lon=${port.lon}`)
      if (res.ok) {
        const data = await res.json()
        setPortAnalysis(data)
      }
    } catch (e) {
      console.error('Port analysis unavailable:', e)
    }
    
    // 2. CRITICAL: Auto-trigger chat to compute PFZ zones + route from this port
    try {
      const chatRes = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `Best PFZ zones from ${port.name}. Show the safest route.`,
          location: [port.lon, port.lat],
        }),
      })
      if (chatRes.ok) {
        const chatData = await chatRes.json()
        
        // Process map actions from orchestrator
        if (chatData.map_actions && Array.isArray(chatData.map_actions)) {
          chatData.map_actions.forEach((action: any) => {
            if (action.type === 'route_to_pfz') {
              setRouteToPfz({ start: action.start, end: action.end })
            } else if (action.type === 'highlight_pfz') {
              setHighlightedPfzId(action.pfz_id)
            } else if (action.type === 'show_pfz_zones') {
              setLivePfzZones(action.zones || [])
            }
          })
        }
        
        // Show the response in the copilot
        addChatMessage({
          role: 'assistant',
          content: chatData.response,
          timestamp: new Date().toISOString(),
        })
        setCopilotOpen(true)
        
        if (chatData.session_id) {
          setSessionId(chatData.session_id)
        }
      }
    } catch (e) {
      console.error('Chat API unavailable:', e)
    } finally {
      setLoading(false)
      setShowFishingHub(false)
    }
  }

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }
  
  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-gradient-to-br from-slate-900/95 to-blue-950/95 p-4 overflow-y-auto">
      <div className="max-w-6xl w-full mx-auto py-8">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-ocean-500 to-ocean-600 rounded-2xl mb-4 shadow-lg shadow-blue-500/20">
            <Anchor className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Choose Your Fishing Hub</h1>
          <p className="text-blue-200 text-lg">Select a location to get real-time marine intelligence and PFZ recommendations.</p>
        </div>

        <motion.div variants={container} initial="hidden" animate="show" className="space-y-12">
          {/* Offshore Section */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <Ship className="w-6 h-6 text-blue-400" />
              <h2 className="text-2xl font-semibold text-white">⚓ Offshore & Deep Sea Fishing Hubs</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {OFFSHORE_HUBS.map((port, idx) => (
                <motion.button
                  key={idx}
                  variants={item}
                  onClick={() => handleSelectPort(port)}
                  disabled={loading}
                  className="text-left p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 hover:bg-white/20 transition-all duration-300 group shadow-xl"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-white group-hover:text-blue-300 transition-colors">{port.name}</h3>
                      <div className="flex items-center gap-1 text-sm text-blue-200 mt-1">
                        <MapPin className="w-3 h-3" />
                        {port.region}
                      </div>
                    </div>
                  </div>
                  <p className="text-gray-300 text-sm mb-4 line-clamp-2">{port.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {port.species.map((s, i) => (
                      <span key={i} className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-200 text-xs font-medium border border-blue-500/30 flex items-center gap-1">
                        <Fish className="w-3 h-3" />
                        {s}
                      </span>
                    ))}
                  </div>
                </motion.button>
              ))}
            </div>
          </section>

          {/* Coastal Section */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <Waves className="w-6 h-6 text-cyan-400" />
              <h2 className="text-2xl font-semibold text-white">🌊 Coastal & Shore Angling Spots</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {COASTAL_SPOTS.map((port, idx) => (
                <motion.button
                  key={idx}
                  variants={item}
                  onClick={() => handleSelectPort(port)}
                  disabled={loading}
                  className="text-left p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 hover:bg-white/20 transition-all duration-300 group shadow-xl"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-white group-hover:text-cyan-300 transition-colors">{port.name}</h3>
                      <div className="flex items-center gap-1 text-sm text-cyan-200 mt-1">
                        <MapPin className="w-3 h-3" />
                        {port.region}
                      </div>
                    </div>
                  </div>
                  <p className="text-gray-300 text-sm mb-4 line-clamp-2">{port.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {port.species.map((s, i) => (
                      <span key={i} className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-200 text-xs font-medium border border-cyan-500/30 flex items-center gap-1">
                        <Fish className="w-3 h-3" />
                        {s}
                      </span>
                    ))}
                  </div>
                </motion.button>
              ))}
            </div>
          </section>
        </motion.div>
        
        <div className="mt-12 text-center pb-8">
          <button 
            onClick={() => setShowFishingHub(false)}
            className="text-gray-400 hover:text-white transition-colors text-sm font-medium"
          >
            Skip to Map →
          </button>
        </div>
      </div>
    </div>
  )
}
