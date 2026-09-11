# ORCA API Documentation

**Base URL:** `http://localhost:8000/api/v1` (development)  
**Version:** 1.0.0  
**Authentication:** Bearer token (JWT)

## Table of Contents

- [Authentication](#authentication)
- [System Endpoints](#system-endpoints)
- [Data Endpoints](#data-endpoints)
- [Agent Endpoints](#agent-endpoints)
- [PFZ Endpoints](#pfz-endpoints)
- [Warning Endpoints](#warning-endpoints)
- [Route Endpoints](#route-endpoints)
- [Admin Endpoints](#admin-endpoints)
- [Error Responses](#error-responses)

## Authentication

Most endpoints require authentication using JWT tokens.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using Token

Include the token in the `Authorization` header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## System Endpoints

### Health Check

Get system health status.

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-09-10T12:00:00Z",
  "sources": {
    "incois_erddap": {
      "ok": true,
      "latency_ms": 120
    },
    "imd_weather": {
      "ok": true,
      "latency_ms": 95
    }
  }
}
```

### List Sources

Get all registered data sources.

```http
GET /api/v1/sources
```

**Response:**
```json
[
  {
    "source_id": "incois_erddap",
    "name": "INCOIS ERDDAP Server",
    "provider": "INCOIS",
    "interface_type": "erddap",
    "capabilities": ["health_check", "get_subset"],
    "variables": ["CHL", "KD490", "TSM"],
    "is_active": true
  }
]
```

### Freshness Report

Get data freshness status for all sources.

```http
GET /api/v1/freshness/report
```

**Response:**
```json
{
  "report_timestamp": "2026-09-10T12:00:00Z",
  "sources": {
    "incois_erddap": {
      "source_name": "INCOIS ERDDAP Server",
      "last_poll_at": "2026-09-10T11:55:00Z",
      "age_seconds": 300,
      "freshness": {
        "critical": "stale",
        "high": "fresh",
        "medium": "fresh"
      },
      "requires_refresh": false
    }
  }
}
```

## Data Endpoints

### Get Latest Data

Get most recent observation/NRT data at a location.

```http
POST /api/v1/data/latest
Content-Type: application/json

{
  "latitude": 19.0760,
  "longitude": 72.8777,
  "radius_km": 50,
  "source_id": "imd_weather"
}
```

**Parameters:**
- `latitude` (required): Latitude in decimal degrees (-90 to 90)
- `longitude` (required): Longitude in decimal degrees (-180 to 180)
- `radius_km` (optional): Search radius in km (default: 50, max: 500)
- `source_id` (required): Data source identifier

**Response:**
```json
{
  "source_id": "imd_weather",
  "dataset_id": "imd_current_weather",
  "variable": "air_temperature",
  "value": 29.5,
  "unit": "celsius",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "observed_at": "2026-09-10T11:30:00Z",
  "retrieved_at": "2026-09-10T12:00:00Z",
  "data_type": "observation",
  "quality_flag": "good",
  "confidence": 0.95
}
```

### Get Data Subset

Query data subset by time, space, and variable.

```http
POST /api/v1/data/subset
Content-Type: application/json

{
  "source_id": "copernicus_marine",
  "dataset_id": "cmems_mod_glo_phy_anfc_0.083deg_P1D-m",
  "variables": ["thetao", "so"],
  "latitude": 19.0760,
  "longitude": 72.8777,
  "radius_km": 50,
  "time_start": "2026-09-09T00:00:00Z",
  "time_end": "2026-09-10T00:00:00Z"
}
```

**Response:**
```json
{
  "query": {
    "source_id": "copernicus_marine",
    "dataset_id": "cmems_mod_glo_phy_anfc_0.083deg_P1D-m",
    "variables": ["thetao", "so"]
  },
  "count": 24,
  "data": [
    {
      "variable": "thetao",
      "value": 28.3,
      "unit": "celsius",
      "latitude": 19.0,
      "longitude": 72.9,
      "observed_at": "2026-09-09T12:00:00Z",
      "data_type": "nrt"
    }
  ],
  "retrieved_at": "2026-09-10T12:00:00Z",
  "freshness": "fresh"
}
```

## Agent Endpoints

### Chat with Agent

Conversational interface with AI agents.

```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "What are the current wave conditions near Mumbai?",
  "session_id": "optional-session-id",
  "mode": "live",
  "context": {}
}
```

**Parameters:**
- `message` (required): User message
- `session_id` (optional): Session ID for conversation continuity
- `mode` (optional): Query mode - "standard" or "live" (default: "standard")
- `context` (optional): Additional context

**Response:**
```json
{
  "message": "Current wave conditions near Mumbai (19.08°N, 72.88°E):\n\n**Safety Status:** ✅ SAFE\nConditions are safe for marine activities\n\n**Weather Conditions:**\n- Wind: 8.5 m/s from 180°\n  ↳ Moderate winds\n- Waves: 1.8 m, period 7s\n  ↳ Slight seas\n...",
  "session_id": "generated-session-id",
  "mode": "live",
  "data_retrieved": true,
  "sources_used": ["imd_weather", "copernicus_marine"],
  "recommendations": [
    "✅ Conditions are safe for marine activities",
    "Best fishing times: Early morning (5-8 AM)"
  ]
}
```

## PFZ Endpoints

### Get PFZ Forecast

Get Potential Fishing Zone recommendations.

```http
POST /api/v1/pfz/forecast
Content-Type: application/json

{
  "latitude": 19.0760,
  "longitude": 72.8777,
  "radius_km": 100,
  "forecast_days": 7,
  "species": ["tuna", "sardine"]
}
```

**Response:**
```json
{
  "query": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "forecast_days": 7
  },
  "forecast_date": "2026-09-10T12:00:00Z",
  "zones": [
    {
      "zone_id": "pfz_001",
      "forecast_date": "2026-09-11T00:00:00Z",
      "latitude": 19.1,
      "longitude": 72.9,
      "suitability_score": 0.85,
      "species": ["tuna"],
      "environmental_factors": {
        "sst": 27.5,
        "chlorophyll": 0.8,
        "current_speed": 0.3
      },
      "confidence": 0.8
    }
  ],
  "metadata": {
    "sources": ["copernicus_marine", "incois_erddap"],
    "generated_at": "2026-09-10T12:00:00Z"
  }
}
```

## Warning Endpoints

### Get Warnings

Get marine warnings and advisories for a location.

```http
POST /api/v1/warnings
Content-Type: application/json

{
  "latitude": 19.0760,
  "longitude": 72.8777,
  "radius_km": 200,
  "severity": ["high", "critical"],
  "warning_types": ["cyclone", "high_wave"]
}
```

**Response:**
```json
{
  "query": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "radius_km": 200
  },
  "count": 1,
  "warnings": [
    {
      "warning_id": "IMD_2026091001",
      "source_id": "imd_weather",
      "warning_type": "high_wave",
      "severity": "high",
      "title": "High Wave Warning - Arabian Sea",
      "description": "Wave heights expected to reach 3-4 meters",
      "issued_at": "2026-09-10T06:00:00Z",
      "valid_until": "2026-09-12T18:00:00Z",
      "affected_region": "Maharashtra coast"
    }
  ],
  "retrieved_at": "2026-09-10T12:00:00Z"
}
```

## Route Endpoints

### Optimize Route

Get optimized marine route.

```http
POST /api/v1/route/optimize
Content-Type: application/json

{
  "start_lat": 19.0760,
  "start_lon": 72.8777,
  "end_lat": 15.4909,
  "end_lon": 73.8278,
  "departure_time": "2026-09-11T06:00:00Z",
  "vessel_type": "fishing",
  "optimize_for": "safety",
  "avoid_zones": ["mpa", "restricted"]
}
```

**Response:**
```json
{
  "route_id": "route_001",
  "segments": [
    {
      "segment_index": 1,
      "start_lat": 19.0760,
      "start_lon": 72.8777,
      "end_lat": 18.5,
      "end_lon": 73.0,
      "distance_km": 65.2,
      "estimated_duration_hours": 5.2,
      "weather_conditions": {
        "wind_speed": 8.5,
        "wave_height": 1.8
      },
      "risk_level": "low"
    }
  ],
  "total_distance_km": 450.5,
  "estimated_duration_hours": 36.5,
  "fuel_estimate": 320.5,
  "safety_score": 0.92,
  "warnings": [
    "High wave warning active near waypoint 3"
  ]
}
```

## Admin Endpoints

### Trigger Source Refresh

Manually trigger data refresh for a source (requires admin role).

```http
POST /api/v1/admin/refresh
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "source_id": "incois_erddap",
  "dataset_id": "optional_dataset_id",
  "priority": "high"
}
```

**Response:**
```json
{
  "task_id": "refresh_task_12345",
  "source_id": "incois_erddap",
  "status": "queued",
  "estimated_completion": "2026-09-10T12:05:00Z"
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "detail": "Additional details (optional)",
  "timestamp": "2026-09-10T12:00:00Z"
}
```

### Common Error Codes

- **400 Bad Request**: Invalid input parameters
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: External service unavailable

### Example Error Response

```json
{
  "error": "ValidationError",
  "message": "Invalid coordinates",
  "detail": "Latitude 95.0 is out of range (-90 to 90)",
  "timestamp": "2026-09-10T12:00:00Z"
}
```

## Rate Limiting

API requests are rate-limited per user:

- **Anonymous users**: 10 requests per minute
- **Authenticated users**: 100 requests per minute
- **Premium users**: 1000 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1694347260
```

## Pagination

Endpoints that return lists support pagination:

```http
GET /api/v1/sources?page=1&size=20
```

Response includes pagination metadata:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

## Webhook Support

ORCA can send notifications to your webhook endpoint for events like:
- New warnings issued
- Data freshness alerts
- PFZ forecast updates

Configure webhooks in your user settings or via the API.
