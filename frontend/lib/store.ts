import { create } from 'zustand'
import { ChatMessage } from './api-client'

export interface MapViewState {
  longitude: number
  latitude: number
  zoom: number
  pitch: number
  bearing: number
}

export interface LayerConfig {
  id: string
  name: string
  category: 'fishing' | 'ocean' | 'weather' | 'hazards' | 'geography' | 'ecology'
  visible: boolean
  opacity: number
  type: 'raster' | 'vector' | 'marker'
  source?: string
  color?: string
}

interface AppStore {
  // Map state
  mapViewState: MapViewState
  setMapViewState: (viewState: Partial<MapViewState>) => void
  
  // Layers
  layers: LayerConfig[]
  toggleLayer: (layerId: string) => void
  setLayerOpacity: (layerId: string, opacity: number) => void
  
  // AI Copilot
  copilotOpen: boolean
  setCopilotOpen: (open: boolean) => void
  chatMessages: ChatMessage[]
  addChatMessage: (message: ChatMessage) => void
  clearChat: () => void
  sessionId: string | null
  setSessionId: (id: string) => void
  
  // Selected location
  selectedLocation: [number, number] | null
  setSelectedLocation: (location: [number, number] | null) => void
  
  // Route to PFZ
  routeToPfz: { start: [number, number], end: [number, number] } | null
  setRouteToPfz: (route: { start: [number, number], end: [number, number] } | null) => void
  highlightedPfzId: string | null
  setHighlightedPfzId: (id: string | null) => void
  livePfzZones: any[]
  setLivePfzZones: (zones: any[]) => void
  
  // Fishing Hub
  activePort: { name: string; lat: number; lon: number; region: string; category: string; description: string; species: string[] } | null
  setActivePort: (port: any) => void
  portAnalysis: any | null
  setPortAnalysis: (analysis: any) => void
  showFishingHub: boolean
  setShowFishingHub: (show: boolean) => void
  
  // Time control
  selectedDate: Date
  setSelectedDate: (date: Date) => void
  
  // UI state
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  
  // Demo mode
  demoMode: boolean
  setDemoMode: (demo: boolean) => void

  // Map click context (Map → Chat connection)
  mapClickContext: { type: string; name?: string; coordinates: [number, number]; properties?: any } | null
  setMapClickContext: (ctx: { type: string; name?: string; coordinates: [number, number]; properties?: any } | null) => void

}

export const useStore = create<AppStore>((set) => ({
  // Map state - centered on India's coastline
  mapViewState: {
    longitude: 72.8258,
    latitude: 18.9220,
    zoom: 9,
    pitch: 0,
    bearing: 0,
  },
  setMapViewState: (viewState) =>
    set((state) => ({
      mapViewState: { ...state.mapViewState, ...viewState },
    })),
  
  // Layers - default configuration
  layers: [
    // Fishing
    { id: 'pfz', name: 'Potential Fishing Zones', category: 'fishing', visible: true, opacity: 0.7, type: 'vector', color: '#10b981' },
    { id: 'fishing-vessels', name: 'Fishing Vessels', category: 'fishing', visible: false, opacity: 1, type: 'marker', color: '#3b82f6' },
    { id: 'catch-data', name: 'Historical Catch Data', category: 'fishing', visible: false, opacity: 0.6, type: 'raster', color: '#6366f1' },
    
    // Ocean
    { id: 'sst', name: 'Sea Surface Temperature', category: 'ocean', visible: true, opacity: 0.7, type: 'raster', color: '#ef4444' },
    { id: 'chlorophyll', name: 'Chlorophyll Concentration', category: 'ocean', visible: true, opacity: 0.7, type: 'raster', color: '#22c55e' },
    { id: 'currents', name: 'Ocean Currents', category: 'ocean', visible: false, opacity: 0.8, type: 'vector', color: '#0ea5e9' },
    { id: 'salinity', name: 'Sea Surface Salinity', category: 'ocean', visible: true, opacity: 0.7, type: 'raster', color: '#06b6d4' },
    
    // Weather
    { id: 'wind', name: 'Wind Speed & Direction', category: 'weather', visible: true, opacity: 0.8, type: 'vector', color: '#8b5cf6' },
    { id: 'waves', name: 'Wave Height', category: 'weather', visible: true, opacity: 0.7, type: 'raster', color: '#6366f1' },
    { id: 'precipitation', name: 'Precipitation', category: 'weather', visible: false, opacity: 0.6, type: 'raster', color: '#64748b' },
    
    // Hazards
    { id: 'cyclones', name: 'Cyclone Tracks', category: 'hazards', visible: true, opacity: 1, type: 'vector', color: '#ef4444' },
    { id: 'warnings', name: 'Active Warnings', category: 'hazards', visible: true, opacity: 1, type: 'marker', color: '#f59e0b' },
    
    // Geography
    { id: 'eez', name: 'Exclusive Economic Zone', category: 'geography', visible: false, opacity: 0.5, type: 'vector', color: '#6366f1' },
    { id: 'ports', name: 'Ports & Harbors', category: 'geography', visible: true, opacity: 1, type: 'marker', color: '#8b5cf6' },
    { id: 'depth', name: 'Bathymetry', category: 'geography', visible: false, opacity: 0.6, type: 'raster', color: '#1e40af' },
    
    // Ecology
    { id: 'coral-reefs', name: 'Coral Reefs', category: 'ecology', visible: false, opacity: 0.7, type: 'vector', color: '#ec4899' },
    { id: 'protected-areas', name: 'Marine Protected Areas', category: 'ecology', visible: false, opacity: 0.5, type: 'vector', color: '#14b8a6' },
  ],
  toggleLayer: (layerId) =>
    set((state) => ({
      layers: state.layers.map((layer) =>
        layer.id === layerId ? { ...layer, visible: !layer.visible } : layer
      ),
    })),
  setLayerOpacity: (layerId, opacity) =>
    set((state) => ({
      layers: state.layers.map((layer) =>
        layer.id === layerId ? { ...layer, opacity } : layer
      ),
    })),
  
  // AI Copilot
  copilotOpen: true,
  setCopilotOpen: (open) => set({ copilotOpen: open }),
  chatMessages: [],
  addChatMessage: (message) =>
    set((state) => ({
      chatMessages: [...state.chatMessages, message],
    })),
  clearChat: () => set({ chatMessages: [], sessionId: null }),
  sessionId: null,
  setSessionId: (id) => set({ sessionId: id }),
  
  // Selected location
  selectedLocation: null,
  setSelectedLocation: (location) => set({ selectedLocation: location }),
  
  // Route to PFZ
  routeToPfz: null,
  setRouteToPfz: (route) => set({ routeToPfz: route }),
  highlightedPfzId: null,
  setHighlightedPfzId: (id) => set({ highlightedPfzId: id }),
  livePfzZones: [],
  setLivePfzZones: (zones) => set({ livePfzZones: zones }),
  
  // Time control
  selectedDate: new Date(),
  setSelectedDate: (date) => set({ selectedDate: date }),
  
  // UI state
  sidebarOpen: false,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  
  // Demo mode — always disabled; backend connects silently in background
  demoMode: false,
  setDemoMode: (_demo) => set({ demoMode: false }),

  // Map click context (Map → Chat connection)
  mapClickContext: null,
  setMapClickContext: (ctx) => set({ mapClickContext: ctx }),

  // Active Port
  activePort: null,
  setActivePort: (port) => set({ activePort: port }),
  portAnalysis: null,
  setPortAnalysis: (analysis) => set({ portAnalysis: analysis }),
  showFishingHub: true,
  setShowFishingHub: (show) => set({ showFishingHub: show }),
}))
