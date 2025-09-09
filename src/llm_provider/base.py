import abc
from typing import Any, Dict

class LLMProvider(abc.ABC):
    """Abstract base class for all LLM providers."""
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    @abc.abstractmethod
    def get_signals(self, prompt: str) -> Dict[str, Any]:
        """Get structured signals (score, rationale, tags, etc.) from the LLM."""
        pass
