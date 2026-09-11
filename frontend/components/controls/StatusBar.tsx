'use client'

import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Activity, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import { formatTimeAgo } from '@/lib/utils'
import { useStore } from '@/lib/store'

export function StatusBar() {
  const { demoMode, setDemoMode } = useStore()

  const { data: health, isError } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.getHealth(),
    refetchInterval: 30000, // 30 seconds
    retry: false,
  })

  useEffect(() => {
    if (health && !isError && demoMode) {
      setDemoMode(false)
    }
  }, [health, isError, demoMode, setDemoMode])

  const { data: sources } = useQuery({
    queryKey: ['sources'],
    queryFn: () => apiClient.getDataSources(),
    refetchInterval: 60000, // 1 minute
    enabled: !demoMode,
  })

  const activeSources = sources?.filter(s => s.status === 'active').length || 0
  const totalSources = sources?.length || 0

  return (
    <div className="fixed bottom-4 left-4 bg-white rounded-lg shadow-lg px-4 py-2 z-40 
                    flex items-center gap-4 text-sm">
      {/* Connection Status */}
      <div className="flex items-center gap-2">
        {demoMode ? (
          <>
            <AlertCircle className="w-4 h-4 text-yellow-500" />
            <span className="text-yellow-700 font-medium">Demo Mode</span>
          </>
        ) : isError ? (
          <>
            <Activity className="w-4 h-4 text-blue-500 animate-pulse" />
            <span className="text-blue-700 font-medium">Syncing live data...</span>
          </>
        ) : (
          <>
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span className="text-green-700 font-medium">Connected</span>
          </>
        )}
      </div>

      {/* Divider */}
      <div className="w-px h-4 bg-gray-300" />

      {/* Data Sources */}
      {!demoMode && sources && (
        <>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-500" />
            <span className="text-gray-700">
              {activeSources}/{totalSources} sources active
            </span>
          </div>

          {/* Divider */}
          <div className="w-px h-4 bg-gray-300" />
        </>
      )}

      {/* Last Update */}
      {health && (
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-500" />
          <span className="text-gray-600">
            Updated {formatTimeAgo(health.timestamp)}
          </span>
        </div>
      )}
    </div>
  )
}
