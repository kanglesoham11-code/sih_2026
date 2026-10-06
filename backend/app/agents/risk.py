from app.services.orchestrator import RiskSafetyEngine

class RiskAgent:
    def health(self) -> tuple[bool, int, str]:
        # Deterministic check: wave > 4 -> NO-GO
        try:
            res = RiskSafetyEngine.calculate_risk(wave_height=5.0, wind_speed=20.0)
            if "DO NOT SAIL" in res:
                return True, 5, 'High-wave input returns NO-GO'
            return False, 5, 'Safety check failed'
        except Exception as e:
            return False, 5, str(e)
