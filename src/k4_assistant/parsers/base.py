from abc import ABC, abstractmethod
from pathlib import Path

from k4_assistant.models import Trade


class TradeParser(ABC):
    @abstractmethod
    def parse(self, path: Path) -> list[Trade]:
        """Read a file and return validated trades."""
