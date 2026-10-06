'use client'

import { useState, useEffect } from 'react'
import { Activity, ChevronDown, CheckCircle, AlertTriangle, XCircle, X } from 'lucide-react'

export default function SystemStatusBarClient({ initialData }: { initialData: any }) {
  const [data, setData] = useState(initialData)
  const [now, setNow] = useState(Date.now())
  const [drawerOpen, setDrawerOpen] = useState(false)

  // Polling for updates every 30s
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/status`)
        if (res.ok) {
          setData(await res.json())
        }
      } catch (e) {
        // Silently fail and let data age
      }
    }
    const interval = setInterval(fetchStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  // Ticking for age counter every 1s
  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(interval)
  }, [])

  // Determine state
  const isColdStart = !data
  const system = data?.system || 'offline'
  
  // Find oldest live source age
  let maxAge = 0
  if (data && data.data_sources) {
    for (const src of data.data_sources) {
      if (src.last_success_at) {
        const age = Math.floor((now - new Date(src.last_success_at).getTime()) / 1000)
        if (age > maxAge) maxAge = age
      }
    }
  }
  
  const formatAge = (s: number) => {
    if (s < 60) return `${s}s`
    if (s < 3600) return `${Math.floor(s/60)}m`
    return `${Math.floor(s/3600)}h`
  }

  // Segment 1
  let seg1Color = 'bg-gray-400'
  let seg1Text = 'ORCA Marine Intelligence'
  if (!isColdStart) {
    if (system === 'live') {
      seg1Color = 'bg-green-500'
      seg1Text = 'SYSTEM LIVE'
    } else if (system === 'degraded') {
      seg1Color = 'bg-amber-500'
      seg1Text = 'SYSTEM DEGRADED'
    } else {
      seg1Color = 'bg-red-500'
      seg1Text = 'SYSTEM OFFLINE'
    }
  }

  // Segment 2
  let seg2Text = 'Refreshing live data...'
  if (!isColdStart) {
    if (system === 'live') {
      seg2Text = `Live marine data pulled from official APIs, auto-refreshed every 60s, last sync ${maxAge}s ago`
    } else if (system === 'degraded') {
      seg2Text = `Showing last verified snapshot (${formatAge(maxAge)})`
    } else {
      seg2Text = `Last verified data ${formatAge(maxAge)} old`
    }
  }

  // Segment 3
  let seg3Text = '10-agent pipeline'
  if (!isColdStart && data.agents_total) {
    seg3Text = `${data.agents_online}/${data.agents_total} AI agents online`
  }

  return (
    <>
      <div 
        role="status" 
        aria-live="polite"
        onClick={() => setDrawerOpen(true)}
        className="fixed top-0 left-0 right-0 z-50 bg-slate-900 text-slate-200 border-b border-slate-700 
                   px-2 sm:px-4 py-1.5 sm:py-2 text-[10px] sm:text-xs cursor-pointer hover:bg-slate-800 transition-colors animate-in slide-in-from-top
                   flex items-center justify-between gap-2 shadow-sm font-mono h-8 sm:h-9"
      >
        <div className="flex items-center gap-1.5 sm:gap-2 font-bold shrink-0">
          <div className={`w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full ${seg1Color} ${system === 'live' ? 'animate-pulse' : ''}`} />
          <span className="hidden sm:inline">{seg1Text}</span>
          <span className="sm:hidden">{system.toUpperCase()}</span>
        </div>
        
        <div className="text-center text-slate-400 truncate flex-1 min-w-0 hidden md:block">
          {seg2Text}
        </div>
        
        <div className="flex items-center gap-1 sm:gap-2 shrink-0">
          <span className="hidden sm:inline">{seg3Text}</span>
          <span className="sm:hidden">{data?.agents_online || 0}/{data?.agents_total || 10} ON</span>
          <ChevronDown className="w-3 h-3 text-slate-500" />
        </div>
      </div>

      {/* Padding to push layout down */}
      <div className="h-8 sm:h-9 w-full" />

      {/* Drawer */}
      {drawerOpen && (
        <div className="fixed inset-0 z-[60] bg-black/60 flex items-start justify-center pt-8 sm:pt-9">
          <div className="bg-white dark:bg-slate-900 w-full max-w-4xl max-h-[80vh] overflow-y-auto rounded-b-xl shadow-2xl border border-slate-200 dark:border-slate-700 animate-in slide-in-from-top p-6 relative">
            <button onClick={() => setDrawerOpen(false)} className="absolute top-4 right-4 p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
              <X className="w-5 h-5 text-slate-500" />
            </button>
            
            <h2 className="text-2xl font-bold mb-2">System Status</h2>
            <p className="text-slate-600 dark:text-slate-400 mb-6 font-medium">Safety decisions are deterministic rules; the LLM only explains.</p>
            
            <div className="grid md:grid-cols-2 gap-8">
              {/* Agents */}
              <div>
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-500" />
                  AI Agents ({data?.agents_online || 0}/{data?.agents_total || 10})
                </h3>
                <div className="bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-slate-100 dark:bg-slate-900 text-xs uppercase text-slate-500">
                      <tr>
                        <th className="px-4 py-2">Agent</th>
                        <th className="px-4 py-2">Latency</th>
                        <th className="px-4 py-2">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                      {data?.agents?.map((a: any) => (
                        <tr key={a.name}>
                          <td className="px-4 py-2 font-medium flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${a.status === 'online' ? 'bg-green-500' : 'bg-red-500'}`} />
                            {a.name}
                          </td>
                          <td className="px-4 py-2 text-slate-500">{a.latency_ms}ms</td>
                          <td className="px-4 py-2 text-slate-500 truncate max-w-[120px]" title={a.check}>{a.check}</td>
                        </tr>
                      ))}
                      {!data?.agents && (
                        <tr><td colSpan={3} className="px-4 py-4 text-center text-slate-500 animate-pulse">Fetching agent status...</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Data Sources */}
              <div>
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-indigo-500" />
                  Data Sources
                </h3>
                <div className="bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-slate-100 dark:bg-slate-900 text-xs uppercase text-slate-500">
                      <tr>
                        <th className="px-4 py-2">Source</th>
                        <th className="px-4 py-2">Kind</th>
                        <th className="px-4 py-2">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                      {data?.data_sources?.map((s: any) => (
                        <tr key={s.name}>
                          <td className="px-4 py-2 font-medium">{s.name}</td>
                          <td className="px-4 py-2">
                            <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold ${s.kind === 'official_api' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30' : 'bg-purple-100 text-purple-700 dark:bg-purple-900/30'}`}>
                              {s.kind.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="px-4 py-2 flex items-center gap-1">
                            {s.status === 'live' && <CheckCircle className="w-3 h-3 text-green-500" />}
                            {s.status === 'cached' && <AlertTriangle className="w-3 h-3 text-amber-500" />}
                            {s.status === 'down' && <XCircle className="w-3 h-3 text-red-500" />}
                            {s.status === 'planned' && <span className="text-slate-400">Roadmap adapter</span>}
                            {s.status !== 'planned' && <span className="capitalize">{s.status}</span>}
                          </td>
                        </tr>
                      ))}
                      {!data?.data_sources && (
                        <tr><td colSpan={3} className="px-4 py-4 text-center text-slate-500 animate-pulse">Fetching source status...</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="mt-8 text-center">
              <a href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/status`} target="_blank" rel="noreferrer" className="text-sm text-blue-500 hover:underline">
                Open API status →
              </a>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
