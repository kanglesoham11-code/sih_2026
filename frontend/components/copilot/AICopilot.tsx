'use client'

import { useState, useRef, useEffect } from 'react'
import { useStore } from '@/lib/store'
import { apiClient, ChatMessage } from '@/lib/api-client'
import { useMutation, useQuery } from '@tanstack/react-query'
import { 
  MessageCircle, 
  Send, 
  X, 
  Minimize2, 
  Maximize2, 
  Trash2,
  Sparkles,
  MapPin,
  AlertTriangle,
} from 'lucide-react'
import { formatTimestamp, generateSessionId } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'

export function AICopilot() {
  const {
    copilotOpen,
    setCopilotOpen,
    chatMessages,
    addChatMessage,
    clearChat,
    sessionId,
    setSessionId,
    selectedLocation,
    setSelectedLocation,
    setMapViewState,
    setRouteToPfz,
    setHighlightedPfzId,
    setLivePfzZones,
    activePort,
    mapClickContext,
    setMapClickContext,
  } = useStore()

  const [input, setInput] = useState('')
  const [isMinimized, setIsMinimized] = useState(false)
  const [vesselClass, setVesselClass] = useState('motorised')
  const [cycloneActive, setCycloneActive] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const { data: statusData } = useQuery({
    queryKey: ['system-status'],
    queryFn: () => fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/status`).then(res => res.json()),
    refetchInterval: 30000
  })
  
  const isColdStart = !statusData

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatMessages])

  // BUG 3 FIX: When map click context changes, auto-add a context message to the chat
  useEffect(() => {
    if (!mapClickContext) return
    
    let contextMsg = ''
    if (mapClickContext.type === 'pfz') {
      contextMsg = `📍 You selected fishing zone: **${mapClickContext.name}** (score: ${mapClickContext.properties?.score}). Ask me anything about this zone.`
    } else if (mapClickContext.type === 'warning') {
      contextMsg = `⚠️ You selected a ${mapClickContext.properties?.severity} warning: **${mapClickContext.name}**. ${mapClickContext.properties?.description || ''}`
    } else if (mapClickContext.type === 'port') {
      contextMsg = `⚓ You selected port: **${mapClickContext.name}**. I can analyze fishing conditions from here.`
    } else {
      contextMsg = `📍 You selected a location at ${mapClickContext.coordinates[1].toFixed(4)}°N, ${mapClickContext.coordinates[0].toFixed(4)}°E.`
    }
    
    addChatMessage({
      role: 'assistant',
      content: contextMsg,
      timestamp: new Date().toISOString(),
    })
    
    // Clear the context after consuming it
    setMapClickContext(null)
  }, [mapClickContext])

  const chatMutation = useMutation({
    mutationFn: (message: string) => {
      if (!sessionId) {
        const newSessionId = generateSessionId()
        setSessionId(newSessionId)
        return apiClient.sendChatMessage({
          message,
          session_id: newSessionId,
          location: activePort ? [activePort.lon, activePort.lat] : selectedLocation || undefined,
          vessel_class: vesselClass,
          cyclone_active: cycloneActive,
        })
      }
      return apiClient.sendChatMessage({
        message,
        session_id: sessionId,
        location: activePort ? [activePort.lon, activePort.lat] : selectedLocation || undefined,
        vessel_class: vesselClass,
        cyclone_active: cycloneActive,
      })
    },
    onSuccess: (data: any) => {
      addChatMessage({
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        evidence: data.evidence,
        agent_trace: data.agent_trace,
      })
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id)
      }
      
      // Handle map actions
      if (data.map_actions && Array.isArray(data.map_actions)) {
        data.map_actions.forEach((action: any) => {
          if (action.type === 'fly_to') {
            const lng = action.longitude ?? action.coordinates?.[0]
            const lat = action.latitude ?? action.coordinates?.[1]
            if (lng && lat) {
              setSelectedLocation([lng, lat])
              setMapViewState({
                longitude: lng,
                latitude: lat,
                zoom: action.zoom || 14,
                pitch: 50,
                bearing: -30
              })
            }
          } else if (action.type === 'route_to_pfz') {
            setRouteToPfz({
              start: action.start,
              end: action.end
            })
          } else if (action.type === 'highlight_pfz') {
            setHighlightedPfzId(action.pfz_id)
          } else if (action.type === 'show_pfz_zones') {
            setLivePfzZones(action.zones || [])
          }
        })
      }
    },
    onError: () => {
      addChatMessage({
        role: 'assistant',
        content: '🔄 **Fetching live data from official APIs!** Please wait a moment while I gather the latest ocean and weather information for you. Try asking again in a few seconds.',
        timestamp: new Date().toISOString(),
      })
    },
  })

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    }

    addChatMessage(userMessage)
    chatMutation.mutate(input)
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const suggestions = [
    'Try this: 🎣 Find me a good fishing spot from here',
    'Try this: 🌊 Is it safe to take my boat out today?',
    'Try this: ⚓ What are the waves and wind like?',
  ]

  if (!copilotOpen) {
    return (
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        onClick={() => setCopilotOpen(true)}
        className="fixed bottom-6 right-6 bg-ocean-500 hover:bg-ocean-600 text-white 
                   rounded-full p-4 shadow-2xl z-50 group"
      >
        <MessageCircle className="w-6 h-6" />
        <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 
                       bg-gray-900 text-white px-3 py-1 rounded-lg text-sm whitespace-nowrap
                       opacity-0 group-hover:opacity-100 transition-opacity">
          Open AI Copilot
        </span>
      </motion.button>
    )
  }

  return (
    <motion.div
      initial={{ x: 400 }}
      animate={{ x: 0 }}
      exit={{ x: 400 }}
      className={`fixed right-0 top-0 h-full bg-white shadow-2xl z-50 flex flex-col
                  ${isMinimized ? 'w-16' : 'w-96'} transition-all duration-300`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-ocean-500 to-ocean-600 text-white">
        {!isMinimized && (
          <>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              <span className="font-semibold">ORCA AI Copilot</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsMinimized(true)}
                className="hover:bg-white/20 p-1 rounded"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setCopilotOpen(false)}
                className="hover:bg-white/20 p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </>
        )}
        {isMinimized && (
          <button
            onClick={() => setIsMinimized(false)}
            className="w-full flex justify-center"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {!isMinimized && (
        <>

          {/* Active Starting Port */}
          {activePort && (
            <div className="bg-emerald-50 border-b border-emerald-200 p-3 text-sm flex justify-between items-center">
              <div>
                <div className="flex items-center gap-2 text-emerald-800">
                  <MapPin className="w-4 h-4" />
                  <span className="font-medium">Starting Port: {activePort.name}</span>
                </div>
                <p className="text-xs text-emerald-700 mt-1">
                  All routes and analysis start from here
                </p>
              </div>
            </div>
          )}
          
          {/* Settings / Overrides */}
          <div className="p-3 bg-gray-50 border-b border-gray-200 text-xs flex flex-col gap-2">
            <div className="flex justify-between items-center">
              <span className="font-medium text-gray-700">Vessel Class:</span>
              <select 
                value={vesselClass} 
                onChange={(e) => setVesselClass(e.target.value)}
                className="bg-white border border-gray-300 rounded px-2 py-1 outline-none focus:border-ocean-500"
              >
                <option value="traditional">Traditional Canoe</option>
                <option value="motorised">Motorised Boat</option>
                <option value="mechanised">Mechanised Trawler</option>
                <option value="deepsea">Deep-sea Vessel</option>
              </select>
            </div>
            <label className="flex items-center justify-between cursor-pointer">
              <span className="font-medium text-gray-700 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3 text-red-500" /> Simulated Cyclone Warning
              </span>
              <input 
                type="checkbox" 
                checked={cycloneActive}
                onChange={(e) => setCycloneActive(e.target.checked)}
                className="accent-red-500"
              />
            </label>
          </div>

          {/* Selected Location */}
          {selectedLocation && !activePort && (
            <div className="bg-blue-50 border-b border-blue-200 p-3 text-sm">
              <div className="flex items-center gap-2 text-blue-800">
                <MapPin className="w-4 h-4" />
                <span className="font-medium">Location Selected</span>
              </div>
              <p className="text-xs text-blue-700 mt-1">
                {selectedLocation[1].toFixed(4)}°N, {selectedLocation[0].toFixed(4)}°E
              </p>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
            {chatMessages.length === 0 && (
              <div className="text-center py-8">
                <Sparkles className="w-12 h-12 text-ocean-500 mx-auto mb-4" />
                <h3 className="font-semibold text-lg mb-2">Welcome to ORCA AI</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Your intelligent marine assistant. Ask me anything about:
                </p>
                <ul className="text-sm text-gray-600 text-left max-w-xs mx-auto space-y-1">
                  <li>• Fishing zone forecasts</li>
                  <li>• Weather conditions</li>
                  <li>• Ocean parameters</li>
                  <li>• Safety warnings</li>
                  <li>• Navigation routes</li>
                </ul>
              </div>
            )}

            <AnimatePresence>
              {chatMessages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-ocean-500 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="text-sm whitespace-pre-wrap break-words">
                      {message.content}
                    </div>
                    {/* Render Evidence if available */}
                    {message.role === 'assistant' && message.evidence && message.evidence.length > 0 && (
                      <div className="mt-3 pt-2 border-t border-gray-300/50">
                        <div className="text-xs font-semibold text-gray-600 mb-1">🔍 Evidence & Sources</div>
                        <ul className="space-y-1">
                          {message.evidence.map((item: any, i: number) => (
                            <li key={i} className="text-[10px] text-gray-600 flex justify-between bg-white/50 px-1.5 py-1 rounded">
                              <span>{item.claim}: <span className="font-medium text-gray-800">{item.value}{item.unit}</span></span>
                              <span className="text-gray-400">[{item.freshness}]</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <div
                      className={`text-xs mt-1 ${
                        message.role === 'user' ? 'text-ocean-100' : 'text-gray-500'
                      }`}
                    >
                      {formatTimestamp(message.timestamp)}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {chatMutation.isPending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <div className="spinner"></div>
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions */}
          {chatMessages.length === 0 && (
            <div className="px-4 pb-3">
              <div className="text-xs font-medium text-gray-500 mb-2">Quick actions:</div>
              <div className="space-y-2">
                {suggestions.slice(0, 3).map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => setInput(suggestion)}
                    className="w-full text-left text-xs p-2 bg-gray-50 hover:bg-gray-100 
                             rounded border border-gray-200 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="border-t p-4 flex flex-col gap-2">
            <div className="flex gap-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={isColdStart ? "Waking the AI agents, ~20s..." : "Ask about fishing zones, weather, safety..."}
                className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 
                         text-sm focus:outline-none focus:ring-2 focus:ring-ocean-500"
                rows={2}
                disabled={chatMutation.isPending || isColdStart}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || chatMutation.isPending || isColdStart}
                className="self-end bg-ocean-500 hover:bg-ocean-600 disabled:bg-gray-300 
                         text-white p-2 rounded-lg transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            
            {/* Status Footer */}
            <div className="text-[10px] text-gray-400 flex justify-between items-center px-1">
              {isColdStart ? (
                <span className="text-amber-500 animate-pulse">Refreshing live data...</span>
              ) : statusData.system === 'live' ? (
                <span>Live · Open-Meteo synced · {statusData.agents_online}/{statusData.agents_total} agents</span>
              ) : statusData.system === 'degraded' ? (
                <span className="text-amber-500">Last verified snapshot</span>
              ) : (
                <span className="text-red-500">System Offline</span>
              )}

              {chatMessages.length > 0 && (
                <button
                  onClick={clearChat}
                  className="text-xs hover:text-gray-600 flex items-center gap-1 transition-colors"
                >
                  <Trash2 className="w-3 h-3" />
                  Clear
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </motion.div>
  )
}
