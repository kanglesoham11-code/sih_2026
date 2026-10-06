'use client'

import { useStore } from '@/lib/store'
import { motion, AnimatePresence } from 'framer-motion'
import { Anchor, Ship, Fish, Waves, MapPin, Radar, ShieldCheck, CloudSun, Route, BarChart3, Compass } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'

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

const LOADING_STEPS = [
  { icon: Radar, text: 'Fetching live ocean data...', color: 'text-blue-400' },
  { icon: CloudSun, text: 'Checking weather conditions...', color: 'text-cyan-400' },
  { icon: ShieldCheck, text: 'Running safety checks...', color: 'text-green-400' },
  { icon: Fish, text: 'Analyzing fish migration patterns...', color: 'text-teal-400' },
  { icon: Compass, text: 'Computing PFZ zones...', color: 'text-indigo-400' },
  { icon: Route, text: 'Finding safest route...', color: 'text-purple-400' },
  { icon: BarChart3, text: 'Generating intelligence report...', color: 'text-amber-400' },
]

function LoadingOverlay({ portName }: { portName: string }) {
  const [stepIndex, setStepIndex] = useState(0)
  const [dots, setDots] = useState('')

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setStepIndex(prev => (prev + 1) % LOADING_STEPS.length)
    }, 2200)
    return () => clearInterval(stepInterval)
  }, [])

  useEffect(() => {
    const dotInterval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.')
    }, 400)
    return () => clearInterval(dotInterval)
  }, [])

  const currentStep = LOADING_STEPS[stepIndex]
  const IconComponent = currentStep.icon

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="fixed inset-0 z-[200] flex items-center justify-center"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md" />

      {/* Content card */}
      <motion.div
        initial={{ scale: 0.85, opacity: 0, y: 30 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 200, damping: 20 }}
        className="relative z-10 w-full max-w-md mx-4"
      >
        <div className="rounded-3xl bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-white/10 shadow-2xl shadow-blue-500/10 p-8 backdrop-blur-xl">
          {/* Pulsing radar ring */}
          <div className="flex justify-center mb-6">
            <div className="relative w-24 h-24 flex items-center justify-center">
              {/* Outer rings */}
              <div className="absolute inset-0 rounded-full border-2 border-blue-500/20 animate-ping" style={{ animationDuration: '2s' }} />
              <div className="absolute inset-2 rounded-full border-2 border-blue-400/30 animate-ping" style={{ animationDuration: '2.5s' }} />
              <div className="absolute inset-4 rounded-full border border-blue-300/40 animate-ping" style={{ animationDuration: '3s' }} />
              {/* Center icon */}
              <div className="relative w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/40">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={stepIndex}
                    initial={{ scale: 0, rotate: -90 }}
                    animate={{ scale: 1, rotate: 0 }}
                    exit={{ scale: 0, rotate: 90 }}
                    transition={{ duration: 0.3 }}
                  >
                    <IconComponent className="w-7 h-7 text-white" />
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>
          </div>

          {/* Port name */}
          <div className="text-center mb-6">
            <h3 className="text-xl font-bold text-white mb-1">Analyzing {portName}</h3>
            <p className="text-blue-300/70 text-sm">ORCA is gathering real-time marine intelligence</p>
          </div>

          {/* Current step text */}
          <div className="min-h-[48px] flex items-center justify-center mb-6">
            <AnimatePresence mode="wait">
              <motion.div
                key={stepIndex}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                transition={{ duration: 0.3 }}
                className={`flex items-center gap-3 text-lg font-medium ${currentStep.color}`}
              >
                <IconComponent className="w-5 h-5 flex-shrink-0" />
                <span>{currentStep.text.replace('...', dots.padEnd(3, '\u00A0'))}</span>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Progress dots */}
          <div className="flex justify-center gap-2">
            {LOADING_STEPS.map((_, i) => (
              <div
                key={i}
                className={`h-1.5 rounded-full transition-all duration-500 ${
                  i === stepIndex
                    ? 'w-8 bg-gradient-to-r from-blue-400 to-cyan-400'
                    : i < stepIndex
                    ? 'w-3 bg-blue-500/50'
                    : 'w-3 bg-white/15'
                }`}
              />
            ))}
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export function FishingHubSelector() {
  const { setActivePort, setShowFishingHub, setSelectedLocation, setMapViewState, setPortAnalysis,
    setRouteToPfz, setHighlightedPfzId, setLivePfzZones, addChatMessage, setSessionId, setCopilotOpen } = useStore()
  const [loading, setLoading] = useState(false)
  const [selectedPortName, setSelectedPortName] = useState('')

  const handleSelectPort = async (port: any) => {
    setLoading(true)
    setSelectedPortName(port.name)
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
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_URL}/api/port-analysis?lat=${port.lat}&lon=${port.lon}`)
      if (res.ok) {
        const data = await res.json()
        setPortAnalysis(data)
      }
    } catch (e) {
      console.error('Port analysis unavailable:', e)
    }
    
    // 2. CRITICAL: Auto-trigger chat to compute PFZ zones + route from this port
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const chatRes = await fetch(`${API_URL}/api/chat`, {
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
      {/* Loading Overlay */}
      <AnimatePresence>
        {loading && <LoadingOverlay portName={selectedPortName} />}
      </AnimatePresence>

      <div className="max-w-6xl w-full mx-auto py-8">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-ocean-500 to-ocean-600 rounded-2xl mb-4 shadow-lg shadow-blue-500/20">
            <Anchor className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Choose Your Fishing Hub</h1>
          <p className="text-blue-200 text-lg mb-2">Select a location to get real-time marine intelligence and PFZ recommendations.</p>
          <p className="text-sm text-blue-300/80 max-w-2xl mx-auto italic font-light">
            Safety-first: any active warning forces an automatic NO-GO. Every answer cites its source and timestamp.
          </p>
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
                  className="text-left p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 hover:bg-white/20 transition-all duration-300 group shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
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
                  className="text-left p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 hover:bg-white/20 transition-all duration-300 group shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
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
            disabled={loading}
            className="text-gray-400 hover:text-white transition-colors text-sm font-medium disabled:opacity-50"
          >
            Skip to Map →
          </button>
        </div>
      </div>
    </div>
  )
}
