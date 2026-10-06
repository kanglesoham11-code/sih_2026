"""
Vessel-class safety thresholds for GO / CAUTION / NO-GO decisions.

IMPORTANT: These are ILLUSTRATIVE prototype values derived from general maritime
safety principles. They MUST be validated with state fisheries departments and
INCOIS guidelines before any operational deployment.

Source: General maritime safety standards + team estimation.
"""

from typing import Dict, Tuple

# Format: (caution_wave, nogo_wave, caution_wind, nogo_wind)
# wave in meters, wind in km/h
VESSEL_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "traditional": {
        "label": "Traditional Canoe",
        "caution_wave_m": 1.0,
        "nogo_wave_m": 1.75,
        "caution_wind_kmh": 25,
        "nogo_wind_kmh": 35,
    },
    "motorised": {
        "label": "Motorised Boat",
        "caution_wave_m": 1.5,
        "nogo_wave_m": 2.5,
        "caution_wind_kmh": 30,
        "nogo_wind_kmh": 45,
    },
    "mechanised": {
        "label": "Mechanised Trawler",
        "caution_wave_m": 2.5,
        "nogo_wave_m": 4.0,
        "caution_wind_kmh": 40,
        "nogo_wind_kmh": 60,
    },
    "deepsea": {
        "label": "Deep-sea Vessel",
        "caution_wave_m": 3.5,
        "nogo_wave_m": 5.5,
        "caution_wind_kmh": 50,
        "nogo_wind_kmh": 70,
    },
}

DEFAULT_VESSEL_CLASS = "motorised"


def get_safety_verdict(
    wave_height: float,
    wind_speed: float,
    vessel_class: str = DEFAULT_VESSEL_CLASS,
    cyclone_active: bool = False,
) -> Tuple[str, str, list]:
    """
    Compute GO / CAUTION / NO-GO for a vessel class.
    
    Returns: (verdict, reason, evidence_items)
    """
    thresholds = VESSEL_THRESHOLDS.get(vessel_class, VESSEL_THRESHOLDS[DEFAULT_VESSEL_CLASS])
    label = thresholds["label"]
    evidence = []
    
    # Cyclone override
    if cyclone_active:
        evidence.append({
            "claim": "Cyclone scenario active",
            "value": "YES",
            "unit": "",
            "source": "User-activated simulated scenario",
            "dataset": "simulated_cyclone_toggle",
            "freshness": "simulated",
        })
        return "NO-GO", f"SIMULATED cyclone warning active — all vessels must stay in port", evidence
    
    # Check wave height
    if wave_height is None or wind_speed is None:
        return "UNVERIFIED", "Missing safety data — do not rely on this", evidence
    
    verdict = "GO"
    reasons = []
    
    evidence.append({
        "claim": f"Wave height for {label}",
        "value": round(wave_height, 2),
        "unit": "m",
        "source": "Open-Meteo Marine API",
        "dataset": "open_meteo_marine",
        "freshness": "live",
    })
    evidence.append({
        "claim": f"Wind speed for {label}",
        "value": round(wind_speed, 1),
        "unit": "km/h",
        "source": "Open-Meteo Weather API",
        "dataset": "open_meteo_weather",
        "freshness": "live",
    })
    
    # Wave check
    if wave_height >= thresholds["nogo_wave_m"]:
        verdict = "NO-GO"
        reasons.append(f"Wave height {wave_height:.1f}m exceeds {label} NO-GO threshold ({thresholds['nogo_wave_m']}m)")
    elif wave_height >= thresholds["caution_wave_m"]:
        if verdict != "NO-GO":
            verdict = "CAUTION"
        reasons.append(f"Wave height {wave_height:.1f}m exceeds {label} CAUTION threshold ({thresholds['caution_wave_m']}m)")
    
    # Wind check
    if wind_speed >= thresholds["nogo_wind_kmh"]:
        verdict = "NO-GO"
        reasons.append(f"Wind speed {wind_speed:.0f}km/h exceeds {label} NO-GO threshold ({thresholds['nogo_wind_kmh']}km/h)")
    elif wind_speed >= thresholds["caution_wind_kmh"]:
        if verdict != "NO-GO":
            verdict = "CAUTION"
        reasons.append(f"Wind speed {wind_speed:.0f}km/h exceeds {label} CAUTION threshold ({thresholds['caution_wind_kmh']}km/h)")
    
    if not reasons:
        reasons.append(f"Conditions within safe limits for {label}")
    
    evidence.append({
        "claim": f"Safety verdict for {label}",
        "value": verdict,
        "unit": "",
        "source": "ORCA deterministic safety engine",
        "dataset": "safety_thresholds_v1",
        "freshness": "live",
    })
    
    return verdict, "; ".join(reasons), evidence
