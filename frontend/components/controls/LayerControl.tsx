'use client'

import { useState } from 'react'
import { useStore } from '@/lib/store'
import { Layers, ChevronDown, ChevronRight, Eye, EyeOff } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const CATEGORY_NAMES = {
  fishing: 'Fishing Zones',
  ocean: 'Ocean Parameters',
  weather: 'Weather & Wind',
  hazards: 'Hazards & Warnings',
  geography: 'Marine Geography',
  ecology: 'Marine Ecology',
}

const CATEGORY_COLORS = {
  fishing: 'text-green-600',
  ocean: 'text-blue-600',
  weather: 'text-sky-600',
  hazards: 'text-red-600',
  geography: 'text-purple-600',
  ecology: 'text-pink-600',
}

export function LayerControl() {
  const { layers, toggleLayer, setLayerOpacity } = useStore()
  const [isOpen, setIsOpen] = useState(false)
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(['fishing', 'hazards'])
  )

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(category)) {
      newExpanded.delete(category)
    } else {
      newExpanded.add(category)
    }
    setExpandedCategories(newExpanded)
  }

  const layersByCategory = layers.reduce((acc, layer) => {
    if (!acc[layer.category]) {
      acc[layer.category] = []
    }
    acc[layer.category].push(layer)
    return acc
  }, {} as Record<string, typeof layers>)

  return (
    <>
      {/* Toggle Button */}
      <motion.button
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-4 top-4 bg-white hover:bg-gray-50 rounded-lg shadow-lg 
                   p-3 z-40 flex items-center gap-2 group"
      >
        <Layers className="w-5 h-5 text-ocean-600" />
        <span className="text-sm font-medium">Layers</span>
        <ChevronRight 
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-90' : ''}`} 
        />
      </motion.button>

      {/* Layer Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, x: -300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -300 }}
            className="fixed left-4 top-20 bg-white rounded-lg shadow-2xl z-40 w-80 max-h-[80vh] 
                       flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="p-4 border-b bg-gradient-to-r from-ocean-50 to-sky-50">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Layers className="w-5 h-5 text-ocean-600" />
                Map Layers
              </h3>
              <p className="text-xs text-gray-600 mt-1">
                Toggle visibility and adjust opacity
              </p>
            </div>

            {/* Categories */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
              {Object.entries(layersByCategory).map(([category, categoryLayers]) => (
                <div key={category} className="mb-2">
                  {/* Category Header */}
                  <button
                    onClick={() => toggleCategory(category)}
                    className="w-full flex items-center justify-between p-2 hover:bg-gray-50 
                             rounded-lg transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      {expandedCategories.has(category) ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                      <span className={`font-medium text-sm ${CATEGORY_COLORS[category as keyof typeof CATEGORY_COLORS]}`}>
                        {CATEGORY_NAMES[category as keyof typeof CATEGORY_NAMES]}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {categoryLayers.filter(l => l.visible).length}/{categoryLayers.length}
                    </span>
                  </button>

                  {/* Layers in Category */}
                  <AnimatePresence>
                    {expandedCategories.has(category) && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="ml-4 space-y-1 overflow-hidden"
                      >
                        {categoryLayers.map((layer) => (
                          <div
                            key={layer.id}
                            className="p-2 rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center justify-between mb-1">
                              <button
                                onClick={() => toggleLayer(layer.id)}
                                className="flex items-center gap-2 flex-1"
                              >
                                {layer.visible ? (
                                  <Eye className="w-4 h-4 text-ocean-600" />
                                ) : (
                                  <EyeOff className="w-4 h-4 text-gray-400" />
                                )}
                                <span className={`text-sm ${layer.visible ? 'text-gray-900' : 'text-gray-400'}`}>
                                  {layer.name}
                                </span>
                              </button>
                              {layer.color && (
                                <div
                                  className="w-3 h-3 rounded-full"
                                  style={{ backgroundColor: layer.color }}
                                />
                              )}
                            </div>

                            {/* Opacity Slider */}
                            {layer.visible && (
                              <div className="flex items-center gap-2 ml-6">
                                <span className="text-xs text-gray-500 w-16">Opacity</span>
                                <input
                                  type="range"
                                  min="0"
                                  max="100"
                                  value={layer.opacity * 100}
                                  onChange={(e) =>
                                    setLayerOpacity(layer.id, Number(e.target.value) / 100)
                                  }
                                  className="flex-1 h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                  style={{
                                    accentColor: layer.color || '#0086e6',
                                  }}
                                />
                                <span className="text-xs text-gray-500 w-8 text-right">
                                  {Math.round(layer.opacity * 100)}%
                                </span>
                              </div>
                            )}
                          </div>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div className="p-3 border-t bg-gray-50 text-xs text-gray-600">
              💡 Click map elements for detailed information
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
