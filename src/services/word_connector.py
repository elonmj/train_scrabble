from typing import Dict, List, Set, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from ..models.board import Board
from ..models.types import Direction
from ..models.gaddag import GADDAG
from ..models.graph import ScrabbleGraph
from ..services.word_validator import WordValidator

PARALLEL_MIN_DISTANCE = 2  # Minimum distance between parallel words
INTERSECT_BONUS = 1.5     # Score multiplier for intersecting words
PARALLEL_PENALTY = 0.7    # Score penalty for parallel words that are too close

@dataclass
class ConnectionPoint:
    """Represents an anchor point for word connections."""
    pos: Tuple[int, int]  # Position on board
    letter: str           # Letter at this point
    word: str            # Word this point belongs to
    index: int           # Index in word
    is_support: bool     # Whether this is a support letter
    
    def get_parallel_distance(self, other: 'ConnectionPoint', direction: Direction) -> int:
        """Calculate the parallel distance to another connection point."""
        if direction == Direction.HORIZONTAL:
            if self.pos[0] == other.pos[0]:  # Same row
                return abs(self.pos[1] - other.pos[1])
            return abs(self.pos[0] - other.pos[0])
        else:  # Vertical
            if self.pos[1] == other.pos[1]:  # Same column
                return abs(self.pos[0] - other.pos[0])
            return abs(self.pos[1] - other.pos[1])

class PotentialConnection(NamedTuple):
    """Represents a potential connection between two points."""
    word: str
    pos: Tuple[int, int]
    direction: Direction
    score: float

class WordConnector:
    """Handles the connection of words on the Scrabble board."""
    
    def __init__(self, board: Board, gaddag: GADDAG, validator: WordValidator, graphe: ScrabbleGraph):
        self.board = board
        self.gaddag = gaddag
        self.validator = validator
        self.graphe = graphe
        
    def get_connection_points(self, word: str, pos: Tuple[int, int], 
                           direction: Direction, lettres_appui: Dict[str, Dict[str, int]]) -> List[ConnectionPoint]:
        """
        Get valid connection points for a word, prioritizing support letters.
        
        Args:
            word: The word to find connection points for
            pos: Current position of the word
            direction: Word's direction
            lettres_appui: Support letter information {word: {letter: position}}
        """
   
        
   
 
    def _score_connection(self, word: str, pos: Tuple[int, int], direction: Direction,
                         point1: ConnectionPoint, point2: ConnectionPoint) -> float:
        """
        Enhanced scoring system that considers:
        - Word length and position
        - Support letter usage
        - Parallel word distances
        - Crossword formations
        - Board coverage and balance
        """
        
        
    def validate_connection(self, connection: PotentialConnection) -> bool:
        """Validate if a connection is legal according to game rules."""
