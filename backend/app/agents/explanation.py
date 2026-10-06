from app.core.config import settings

class ExplanationAgent:
    def health(self) -> tuple[bool, int, str]:
        if settings.GROQ_API_KEY:
            return True, 10, 'LLM configured'
        return False, 0, 'No LLM API key'
