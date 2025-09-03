from abc import ABC, abstractmethod
from typing import List   

class ChunkingStrategy(ABC):
    """Abstract base class for all chunking strategies."""
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass

