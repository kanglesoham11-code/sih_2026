const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  evidence?: any[]
  agent_trace?: any[]
}

export interface ChatRequest {
  message: string
  session_id?: string
  location?: [number, number]
  vessel_class?: string
  cyclone_active?: boolean
}

export interface ChatResponse {
  response: string
  session_id: string
  suggestions?: string[]
  map_actions?: any[]
  evidence?: any[]
  agent_trace?: any[]
}

export interface HealthStatus {
  status: string
  version: string
  timestamp: string
  services: {
    database: boolean
    redis: boolean
    celery: boolean
  }
}

export interface DataSource {
  id: string
  name: string
  type: string
  status: 'active' | 'degraded' | 'down'
  last_update: string
  coverage_area: any
}

export interface PFZZone {
  id: string
  geometry: any
  properties: {
    forecast_date: string
    valid_from: string
    valid_to: string
    confidence_score: number
    expected_catch?: string
    fish_species?: string[]
    depth_range?: string
    sst_range?: string
  }
}

export interface Observation {
  id: string
  type: string
  location: [number, number]
  timestamp: string
  parameters: Record<string, any>
  source: string
}

export interface Warning {
  id: string
  type: 'cyclone' | 'swell' | 'wind' | 'other'
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  affected_area: any
  issued_at: string
  valid_until: string
}

class APIClient {
  private baseURL: string

  constructor() {
    this.baseURL = API_URL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Health check
  async getHealth(): Promise<HealthStatus> {
    return this.request<HealthStatus>('/health')
  }

  // Chat
  async sendChatMessage(data: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Data sources
  async getDataSources(): Promise<DataSource[]> {
    return this.request<DataSource[]>('/api/sources')
  }

  // PFZ Zones
  async getPFZZones(params?: {
    min_lat?: number
    max_lat?: number
    min_lon?: number
    max_lon?: number
    start_date?: string
    end_date?: string
  }): Promise<PFZZone[]> {
    const queryParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }
    const query = queryParams.toString()
    return this.request<PFZZone[]>(`/api/pfz${query ? `?${query}` : ''}`)
  }

  // Observations
  async getObservations(params: {
    lat: number
    lon: number
    radius_km?: number
    start_time?: string
    end_time?: string
    types?: string[]
  }): Promise<Observation[]> {
    const queryParams = new URLSearchParams()
    queryParams.append('lat', String(params.lat))
    queryParams.append('lon', String(params.lon))
    if (params.radius_km) queryParams.append('radius_km', String(params.radius_km))
    if (params.start_time) queryParams.append('start_time', params.start_time)
    if (params.end_time) queryParams.append('end_time', params.end_time)
    if (params.types) {
      params.types.forEach(type => queryParams.append('types', type))
    }
    
    return this.request<Observation[]>(`/api/observations?${queryParams.toString()}`)
  }

  // Warnings
  async getWarnings(params?: {
    severity?: string
    type?: string
    active_only?: boolean
  }): Promise<Warning[]> {
    const queryParams = new URLSearchParams()
    if (params?.severity) queryParams.append('severity', params.severity)
    if (params?.type) queryParams.append('type', params.type)
    if (params?.active_only) queryParams.append('active_only', 'true')
    
    const query = queryParams.toString()
    return this.request<Warning[]>(`/api/warnings${query ? `?${query}` : ''}`)
  }

  // Recommendations
  async getRecommendations(params: {
    lat: number
    lon: number
    vessel_type?: string
    activity?: string
  }): Promise<any> {
    const queryParams = new URLSearchParams()
    queryParams.append('lat', String(params.lat))
    queryParams.append('lon', String(params.lon))
    if (params.vessel_type) queryParams.append('vessel_type', params.vessel_type)
    if (params.activity) queryParams.append('activity', params.activity)
    
    return this.request(`/api/recommendations?${queryParams.toString()}`)
  }
}

export const apiClient = new APIClient()
