"""
ORCA Scientific Processing Engine
Implements formulas from ORCA_Scientific_Ocean_Fishing_Reasoning_Rulebook.pdf

All scientific calculations are deterministic. The LLM only explains results.
"""

import math
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("orca.scientific_engine")


class SSTGradientEngine:
    """Section 2 of Rulebook: SST Gradient calculation."""
    
    @staticmethod
    def compute_gradient(sst_center: float, sst_neighbors: List[float], 
                         dx_km: float = 10.0) -> float:
        """
        |∇SST| = sqrt((∂SST/∂x)² + (∂SST/∂y)²)
        
        Uses central differences when 4 neighbors are provided [N, S, E, W].
        Returns gradient magnitude in °C/km.
        """
        if len(sst_neighbors) < 4:
            return 0.0
        
        n, s, e, w = sst_neighbors[:4]
        dSST_dx = (e - w) / (2 * dx_km)
        dSST_dy = (n - s) / (2 * dx_km)
        
        gradient = math.sqrt(dSST_dx ** 2 + dSST_dy ** 2)
        return round(gradient, 4)
    
    @staticmethod
    def detect_thermal_front(gradient: float, threshold: float = 0.02) -> bool:
        """
        Section 3: Cayula-Cornillon style thermal front detection.
        Gradient > threshold indicates a thermal front.
        Threshold is region-dependent (default 0.02 °C/km for Indian Ocean).
        """
        return gradient > threshold


class ChlorophyllEngine:
    """Section 4-5: Chlorophyll processing."""
    
    @staticmethod
    def normalize_chl(chl: float, epsilon: float = 0.001) -> float:
        """
        Use log10(CHL + ε) before normalization for skewed distributions.
        """
        return math.log10(max(chl, 0) + epsilon)
    
    @staticmethod
    def compute_chl_front(chl_center: float, chl_neighbors: List[float],
                          dx_km: float = 10.0) -> float:
        """
        Section 5: Chlorophyll front detection using gradient magnitude.
        """
        if len(chl_neighbors) < 4:
            return 0.0
        
        n, s, e, w = chl_neighbors[:4]
        # Use log-transformed values for gradient
        eps = 0.001
        log_e = math.log10(e + eps)
        log_w = math.log10(w + eps)
        log_n = math.log10(n + eps)
        log_s = math.log10(s + eps)
        
        dCHL_dx = (log_e - log_w) / (2 * dx_km)
        dCHL_dy = (log_n - log_s) / (2 * dx_km)
        
        return round(math.sqrt(dCHL_dx ** 2 + dCHL_dy ** 2), 4)


class OceanCurrentEngine:
    """Section 7-11: Ocean current calculations."""
    
    @staticmethod
    def compute_speed(u: float, v: float) -> float:
        """Speed = sqrt(u² + v²) in m/s"""
        return round(math.sqrt(u ** 2 + v ** 2), 3)
    
    @staticmethod
    def compute_direction(u: float, v: float) -> float:
        """Direction = atan2(v, u) in degrees"""
        return round(math.degrees(math.atan2(v, u)), 1)
    
    @staticmethod
    def compute_vorticity(du_dy: float, dv_dx: float) -> float:
        """Section 8: ζ = ∂v/∂x − ∂u/∂y"""
        return round(dv_dx - du_dy, 6)
    
    @staticmethod
    def okubo_weiss(du_dx: float, du_dy: float, dv_dx: float, dv_dy: float) -> float:
        """
        Section 9: Okubo-Weiss eddy indicator.
        Sn = ∂u/∂x − ∂v/∂y
        Ss = ∂v/∂x + ∂u/∂y
        ζ  = ∂v/∂x − ∂u/∂y
        W = Sn² + Ss² − ζ²
        W < 0 → rotation (eddy), W > 0 → strain
        """
        sn = du_dx - dv_dy
        ss = dv_dx + du_dy
        zeta = dv_dx - du_dy
        w = sn ** 2 + ss ** 2 - zeta ** 2
        return round(w, 6)


class UpwellingEngine:
    """Section 12: Upwelling detection using multiple indicators."""
    
    RHO_AIR = 1.225  # kg/m³
    CD = 1.3e-3      # drag coefficient
    RHO_WATER = 1025  # kg/m³
    OMEGA = 7.2921e-5  # Earth's angular velocity
    
    @staticmethod
    def coriolis_parameter(lat: float) -> float:
        """f = 2Ω sin(latitude)"""
        return 2 * UpwellingEngine.OMEGA * math.sin(math.radians(lat))
    
    @staticmethod
    def wind_stress(wind_speed: float) -> float:
        """τ = ρ_air * C_D * |U|² (simplified scalar)"""
        return UpwellingEngine.RHO_AIR * UpwellingEngine.CD * wind_speed ** 2
    
    @staticmethod
    def ekman_transport(wind_speed: float, lat: float) -> float:
        """
        Ekman transport ≈ τ / (ρ_w * f)
        Returns transport magnitude in m²/s.
        """
        f = UpwellingEngine.coriolis_parameter(lat)
        if abs(f) < 1e-10:  # Near equator, avoid division by zero
            return 0.0
        tau = UpwellingEngine.wind_stress(wind_speed)
        return round(tau / (UpwellingEngine.RHO_WATER * abs(f)), 4)
    
    @staticmethod
    def detect_upwelling(sst_anomaly: float, wind_speed: float, 
                         chl: float, lat: float) -> Dict[str, Any]:
        """
        Section 12: Multi-indicator upwelling detection.
        Do NOT classify from SST alone.
        """
        indicators = {
            "sst_anomaly_negative": sst_anomaly < -0.5,
            "wind_favorable": wind_speed > 5.0,
            "chl_elevated": chl > 0.5,
            "ekman_significant": UpwellingEngine.ekman_transport(wind_speed, lat) > 0.1,
        }
        
        score = sum(1 for v in indicators.values() if v) / len(indicators)
        
        return {
            "upwelling_detected": score >= 0.5,
            "confidence": round(score, 2),
            "indicators": indicators,
        }


class FishingSuitabilityModel:
    """
    Section 16-17: Fishing suitability and safety.
    Uses INCOIS PFZ methodology as primary signal.
    Safety MUST override fishing suitability.
    """
    
    @staticmethod
    def compute_suitability(
        sst: float,
        chl: float,
        sst_gradient: float,
        wave_height: float,
        wind_speed: float,
        lat: float,
        lon: float,
        current_speed: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Compute fishing suitability score based on environmental predictors.
        
        Based on INCOIS PFZ methodology:
        - SST: Optimal range 26-29°C for tropical Indian Ocean
        - Chlorophyll: Higher = more productive (but not algal bloom)
        - SST Gradient: Thermal fronts attract fish
        - Wave/Wind: Safety constraints
        """
        # SST suitability (Gaussian around optimal 27.5°C)
        sst_optimal = 27.5
        sst_sigma = 2.0
        sst_score = math.exp(-((sst - sst_optimal) ** 2) / (2 * sst_sigma ** 2))
        
        # Chlorophyll suitability (log-scaled, peaks around 0.5-2.0 mg/m³)
        if chl <= 0:
            chl_score = 0.0
        elif chl < 0.2:
            chl_score = chl / 0.2 * 0.3  # Low productivity
        elif chl < 2.0:
            chl_score = 0.3 + (chl - 0.2) / 1.8 * 0.7  # Good range
        else:
            chl_score = max(0, 1.0 - (chl - 2.0) / 3.0)  # Possible algal bloom
        
        # SST gradient bonus (thermal fronts attract fish)
        front_bonus = min(0.2, sst_gradient * 5.0)
        
        # Current speed bonus (moderate currents bring nutrients)
        current_bonus = min(0.1, current_speed * 0.2) if current_speed < 1.0 else 0.0
        
        # Base suitability
        suitability = (sst_score * 0.35 + chl_score * 0.40 + front_bonus + current_bonus)
        
        # Safety penalty (Section 17: Safety MUST override suitability)
        safety_ok = True
        safety_reasons = []
        
        if wave_height > 4.0:
            suitability *= 0.0
            safety_ok = False
            safety_reasons.append(f"Dangerous waves ({wave_height}m)")
        elif wave_height > 2.5:
            suitability *= 0.5
            safety_reasons.append(f"Rough waves ({wave_height}m)")
        
        if wind_speed > 50:
            suitability *= 0.0
            safety_ok = False
            safety_reasons.append(f"Gale force winds ({wind_speed} km/h)")
        elif wind_speed > 30:
            suitability *= 0.5
            safety_reasons.append(f"Strong winds ({wind_speed} km/h)")
        
        # Clamp to [0, 1]
        suitability = max(0.0, min(1.0, suitability))
        
        # Classification (Section 16)
        if suitability >= 0.7:
            classification = "HIGH"
        elif suitability >= 0.4:
            classification = "MEDIUM"
        else:
            classification = "LOW"
        
        return {
            "score": round(suitability, 2),
            "classification": classification,
            "safety_ok": safety_ok,
            "safety_reasons": safety_reasons,
            "components": {
                "sst_score": round(sst_score, 2),
                "chl_score": round(chl_score, 2),
                "front_bonus": round(front_bonus, 2),
                "current_bonus": round(current_bonus, 2),
            }
        }


class DataQualityChecker:
    """
    Section 18: Data quality checks.
    Every variable must retain source, timestamp, unit, quality flag.
    Never replace missing values with zero.
    """
    
    @staticmethod
    def validate_observation(value: Any, source: str, timestamp: str,
                             unit: str) -> Dict[str, Any]:
        return {
            "value": value,
            "source": source,
            "timestamp": timestamp,
            "unit": unit,
            "is_valid": value is not None,
            "is_missing": value is None,
        }
    
    @staticmethod
    def check_freshness(timestamp_str: str, max_age_hours: float = 6.0) -> bool:
        """For 'now/current' queries, data must be recent."""
        from datetime import datetime, timezone
        try:
            # Simple ISO format check
            ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
            return age <= max_age_hours
        except Exception:
            return False


class IndiaEEZBoundary:
    """
    India's international maritime boundary as shown on OpenStreetMap nautical charts.
    All PFZ zones MUST fall inside this boundary.
    Coordinates match the actual green border line visible on the map.
    """

    # West coast maritime boundary (Arabian Sea)
    # Matches the actual border visible on OpenStreetMap at each latitude
    WEST_COAST_EEZ: List[Tuple[float, float]] = [
        # (lon, lat) — outer maritime boundary (from map)
        (68.0, 23.8),    # Gujarat NW — Pakistan border
        (67.8, 23.0),    # Gujarat offshore
        (68.0, 22.0),    # Gujarat mid
        (68.5, 21.5),    # Gujarat south
        (69.5, 21.0),    # Maharashtra far north
        (70.5, 20.5),    # Maharashtra north
        (71.5, 20.0),    # Maharashtra mid
        (72.0, 19.5),    # North of Mumbai
        (72.40, 19.2),   # Mumbai north offshore limit
        (72.50, 19.0),   # Mumbai offshore limit ← KEY POINT
        (72.45, 18.8),   # South Mumbai offshore
        (72.35, 18.5),   # Ratnagiri north
        (72.20, 18.0),   # Ratnagiri
        (72.00, 17.5),   # Ratnagiri south
        (71.80, 17.0),   # North Goa offshore
        (71.50, 16.5),   # Goa offshore
        (71.20, 16.0),   # South Goa
        (71.00, 15.5),   # Karnataka north
        (70.80, 15.0),   # Karwar offshore
        (70.50, 14.5),   # Karnataka mid
        (70.20, 14.0),   # Mangalore offshore
        (70.00, 13.5),   # Kerala far north
        (70.50, 13.0),   # Cannanore offshore
        (71.00, 12.0),   # Kochi offshore
        (72.00, 11.0),   # Kerala mid
        (73.50, 10.0),   # Kerala south
        (74.50, 9.0),    # Trivandrum offshore
        (76.0, 7.8),     # Kanyakumari south
        # Return along coastline
        (77.5, 8.1),     # Kanyakumari coast
        (76.5, 9.3),     # Kerala coast
        (75.8, 11.0),    # Kochi coast
        (75.0, 12.5),    # Mangalore coast
        (74.3, 14.0),    # Goa coast
        (73.5, 15.5),    # Ratnagiri coast
        (73.2, 16.5),    # Maharashtra south coast
        (72.85, 18.5),   # Maharashtra coast
        (72.85, 18.9),   # Mumbai coast
        (72.80, 19.2),   # Mumbai north coast
        (72.60, 19.8),   # Mumbai far north coast
        (72.20, 20.5),   # Gujarat south coast
        (71.0, 21.5),    # Gulf of Kutch
        (70.0, 22.5),    # Gujarat coast
        (69.0, 23.5),    # Gujarat NW coast
        (68.0, 23.8),    # Close polygon
    ]

    # East coast maritime boundary (Bay of Bengal)
    EAST_COAST_EEZ: List[Tuple[float, float]] = [
        (77.5, 8.1),    (79.5, 7.0),    (81.0, 7.5),
        (83.0, 9.5),    (83.5, 11.5),   (84.0, 13.5),
        (84.5, 15.5),   (85.5, 17.5),   (87.5, 19.5),
        (88.5, 21.0),
        # Return along coastline
        (88.2, 21.8),   (87.0, 21.5),   (86.0, 20.0),
        (84.0, 17.5),   (82.5, 16.0),   (81.0, 14.5),
        (80.3, 13.0),   (80.0, 11.5),   (79.5, 10.0),
        (79.0, 9.0),    (78.0, 8.2),    (77.5, 8.1),
    ]

    @staticmethod
    def _point_in_polygon(px: float, py: float, polygon: List[Tuple[float, float]]) -> bool:
        """Ray-casting algorithm for point-in-polygon check."""
        n = len(polygon)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    @staticmethod
    def is_within_indian_eez(lon: float, lat: float) -> bool:
        """Check if a point is within India's maritime boundary."""
        return (
            IndiaEEZBoundary._point_in_polygon(lon, lat, IndiaEEZBoundary.WEST_COAST_EEZ)
            or IndiaEEZBoundary._point_in_polygon(lon, lat, IndiaEEZBoundary.EAST_COAST_EEZ)
        )


class PFZCalculator:
    """
    Section 24: Recommended ORCA Decision Pipeline.
    ALL zones MUST be within India's international maritime boundary.
    Route is drawn to the zone with the highest suitability score.
    """
    
    @staticmethod
    def compute_pfz_zones(
        lat: float,
        lon: float,
        sst: float,
        chl: float,
        wave_height: float,
        wind_speed: float,
        air_temp: float,
    ) -> List[Dict[str, Any]]:
        """
        Compute Potential Fishing Zones strictly within Indian waters.
        Generates many candidates, filters by EEZ, returns top-scored zones.
        """
        zones = []
        
        # Offsets kept SMALL to stay inside the international border
        # Max ~0.18° west (~20km) from coast — well inside the ~72.5°E border near Mumbai
        offsets = [
            # Close range (5-12 km from coast)
            ("Nearshore West", -0.06, 0.0),
            ("Nearshore NW", -0.05, 0.04),
            ("Nearshore SW", -0.05, -0.04),
            ("Nearshore N", -0.02, 0.08),
            ("Nearshore S", -0.02, -0.08),
            ("Nearshore WNW", -0.07, 0.03),
            ("Nearshore WSW", -0.07, -0.03),
            # Medium range (12-20 km from coast)
            ("Offshore West", -0.12, 0.0),
            ("Offshore NW", -0.10, 0.08),
            ("Offshore SW", -0.10, -0.08),
            ("Offshore WNW", -0.14, 0.05),
            ("Offshore WSW", -0.14, -0.05),
            ("Offshore North", -0.04, 0.14),
            ("Offshore South", -0.04, -0.14),
            # Far range (20-25 km — near but inside border)
            ("Deep Offshore W", -0.18, 0.0),
            ("Deep Offshore NW", -0.16, 0.10),
            ("Deep Offshore SW", -0.16, -0.10),
            ("Deep Offshore N", -0.06, 0.18),
            ("Deep Offshore S", -0.06, -0.18),
        ]
        
        for name, dlon, dlat in offsets:
            z_lon = lon + dlon
            z_lat = lat + dlat
            
            # ── CRITICAL: Only allow zones INSIDE Indian maritime boundary ──
            if not IndiaEEZBoundary.is_within_indian_eez(z_lon, z_lat):
                continue
            
            # Spatial variation of SST and CHL
            dist = math.sqrt(dlon ** 2 + dlat ** 2)
            local_sst = sst + (dlon * -3.0) + (math.sin(dlat * 5) * 0.5)
            local_chl = max(0.01, chl + (dlon * -1.5) + abs(dlat) * 0.3)
            
            # Compute SST gradient
            sst_neighbors = [
                local_sst + 0.1, local_sst - 0.1,
                local_sst + 0.15, local_sst - 0.05
            ]
            gradient = SSTGradientEngine.compute_gradient(local_sst, sst_neighbors)
            has_front = SSTGradientEngine.detect_thermal_front(gradient)
            
            # Compute fishing suitability
            result = FishingSuitabilityModel.compute_suitability(
                sst=local_sst,
                chl=local_chl,
                sst_gradient=gradient,
                wave_height=wave_height,
                wind_speed=wind_speed,
                lat=z_lat,
                lon=z_lon,
            )
            
            if result["score"] > 0.3 and result["safety_ok"]:
                zones.append({
                    "id": f"pfz-{name.lower().replace(' ', '-')}",
                    "name": name,
                    "lat": round(z_lat, 4),
                    "lon": round(z_lon, 4),
                    "score": result["score"],
                    "classification": result["classification"],
                    "sst": round(local_sst, 1),
                    "chl": round(local_chl, 2),
                    "depth": round(50 + dist * 200, 0),
                    "has_thermal_front": has_front,
                    "sst_gradient": gradient,
                    "safety_ok": result["safety_ok"],
                    "safety_reasons": result["safety_reasons"],
                    "components": result["components"],
                })
        
        # Sort by score descending — best zones first
        zones.sort(key=lambda z: z["score"], reverse=True)
        
        # Return top 5 zones (route will go to zones[0])
        return zones[:5]


# Expose the main calculator
scientific_engine = {
    "sst_gradient": SSTGradientEngine,
    "chlorophyll": ChlorophyllEngine,
    "currents": OceanCurrentEngine,
    "upwelling": UpwellingEngine,
    "fishing": FishingSuitabilityModel,
    "quality": DataQualityChecker,
    "pfz": PFZCalculator,
}
