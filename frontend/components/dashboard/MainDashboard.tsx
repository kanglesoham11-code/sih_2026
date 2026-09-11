'use client'

import { MainMap } from '@/components/map/MainMap'
import { AICopilot } from '@/components/copilot/AICopilot'
import { SearchBar } from '@/components/controls/SearchBar'
import { StatusBar } from '@/components/controls/StatusBar'
import { LayerControl } from '@/components/controls/LayerControl'
import { InfoPanel } from '@/components/panels/InfoPanel'
import { TimeControl } from '@/components/controls/TimeControl'
import { FishingHubSelector } from '@/components/panels/FishingHubSelector'
import { useStore } from '@/lib/store'
import { Anchor } from 'lucide-react'

export function MainDashboard() {
  const { demoMode, setDemoMode, showFishingHub, setShowFishingHub } = useStore()

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-gray-900">
      {/* Demo Mode Banner */}
      {demoMode && (
        <div className="absolute top-0 left-0 right-0 bg-yellow-500 text-gray-900 
                      px-4 py-2 text-center text-sm font-medium z-50 flex items-center 
                      justify-center gap-4">
          <span>
            🌊 ORCA Demo Mode - Backend connection required for live data
          </span>
          <button
            onClick={() => setDemoMode(false)}
            className="bg-white px-3 py-1 rounded text-xs hover:bg-gray-100"
          >
            Try Connect
          </button>
        </div>
      )}

      {/* Main Map - 90% of viewport */}
      <div className={`absolute inset-0 ${demoMode ? 'top-10' : 'top-0'}`}>
        <MainMap />
      </div>

      {/* Top Left - Search and Hubs Button */}
      <div className="absolute top-20 left-20 z-30 flex gap-4">
        <div className="w-96">
          <SearchBar />
        </div>
        <button
          onClick={() => setShowFishingHub(true)}
          className="bg-white/90 backdrop-blur px-4 py-2 rounded-lg shadow-lg border border-gray-200 
                     flex items-center gap-2 hover:bg-white transition-colors"
        >
          <Anchor className="w-5 h-5 text-blue-600" />
          <span className="font-medium text-gray-700">Fishing Hubs</span>
        </button>
      </div>

      {/* Full Screen Overlay for Fishing Hub Selection */}
      {showFishingHub && <FishingHubSelector />}

      {/* Left Side - Layer Control */}
      <LayerControl />

      {/* Right Side - AI Copilot */}
      <AICopilot />

      {/* Bottom - Status Bar */}
      <StatusBar />

      {/* Bottom Right - Time Control */}
      <TimeControl />

      {/* Info Panel (when location selected) */}
      <InfoPanel />

      {/* Branding */}
      <div className="absolute top-4 right-20 z-30 bg-white/90 backdrop-blur rounded-lg 
                    shadow-lg px-4 py-2 flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-ocean-500 to-ocean-600 
                        rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">🌊</span>
          </div>
          <div>
            <div className="font-bold text-ocean-600 text-sm">ORCA</div>
            <div className="text-xs text-gray-600">Marine Intelligence</div>
          </div>
        </div>
      </div>
    </div>
  )
}
