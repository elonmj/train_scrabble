from enum import Enum
from dataclasses import dataclass

class SquareType(Enum):
    """Types de cases spéciales sur le plateau."""
    NORMAL = 0
    DOUBLE_LETTER = 1
    TRIPLE_LETTER = 2
    DOUBLE_WORD = 3
    TRIPLE_WORD = 4
    START = 5  # Case centrale avec étoile

class Direction(Enum):
    """Direction de placement des mots sur le plateau."""
    HORIZONTAL = 'H'
    VERTICAL = 'V'

@dataclass
class Move:
    """Représente un coup possible sur le plateau."""
    word: str              # Le mot formé
    row: int              # Ligne de départ
    col: int              # Colonne de départ
    direction: Direction   # Direction du placement
    score: int = 0        # Score du coup

    def __str__(self) -> str:
        return f"{self.word} en {chr(65+self.row)}{self.col+1} {self.direction.value} ({self.score} pts)"
