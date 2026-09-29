import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format, formatDistanceToNow } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTimestamp(timestamp: string): string {
  try {
    const date = new Date(timestamp)
    return format(date, 'MMM d, yyyy HH:mm')
  } catch {
    return timestamp
  }
}

export function formatTimeAgo(timestamp: string): string {
  try {
    const date = new Date(timestamp)
    return formatDistanceToNow(date, { addSuffix: true })
  } catch {
    return timestamp
  }
}

export function getFreshnessColor(timestamp: string): string {
  const now = Date.now()
  const time = new Date(timestamp).getTime()
  const diffHours = (now - time) / (1000 * 60 * 60)
  
  if (diffHours < 1) return 'text-green-500'
  if (diffHours < 6) return 'text-blue-500'
  if (diffHours < 24) return 'text-yellow-500'
  if (diffHours < 72) return 'text-orange-500'
  return 'text-red-500'
}

export function getFreshnessLabel(timestamp: string): string {
  const now = Date.now()
  const time = new Date(timestamp).getTime()
  const diffHours = (now - time) / (1000 * 60 * 60)
  
  if (diffHours < 1) return 'Live'
  if (diffHours < 6) return 'Fresh'
  if (diffHours < 24) return 'Recent'
  if (diffHours < 72) return 'Aging'
  return 'Stale'
}

export function coordinateToString(coord: [number, number]): string {
  const [lon, lat] = coord
  const latDir = lat >= 0 ? 'N' : 'S'
  const lonDir = lon >= 0 ? 'E' : 'W'
  return `${Math.abs(lat).toFixed(4)}°${latDir}, ${Math.abs(lon).toFixed(4)}°${lonDir}`
}

export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}
