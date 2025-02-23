from typing import List, Optional, Tuple
from ..models.board import Board
from .move_generator import MoveGenerator
from .score_calculator import ScoreCalculator
from .word_validator import WordValidator
from ..models.types import Move, Direction
from ..models.gaddag import GADDAG

class GameManager:
    """Gère la logique du jeu Scrabble."""
    
    def __init__(self, board: Board, gaddag: GADDAG):
        self.board = board
        self.gaddag = gaddag
        self.validator = WordValidator(board, gaddag)
        self.score_calculator = ScoreCalculator(board)
        self.move_generator = MoveGenerator(gaddag, board)

    def place_move(self, move: Move) -> Optional[int]:
        """Orchestre le placement d'un coup."""
        # 1. Validation
        if not self.validator.is_valid_word(move.word):
            return None
            
        if not self.validator.is_valid_move(move.word, move.row, move.col, move.direction):
            return None
        
        # 2. Calcul du score
        score = self.score_calculator.calculate_move_score(move)
        
        # 3. Application du coup
        self.board.apply_move(move, score)
        
        return score

    def suggest_moves(self, rack: str, limit: int = 5) -> List[Tuple[Move, int]]:
        """Suggère les meilleurs coups possibles pour un rack donné."""
        # Génère tous les coups possibles
        moves = self.move_generator.generate_moves(rack)
        
        # Simule le score pour chaque coup
        scored_moves = [
            (move, self.score_calculator.simulate_move_score(move))
            for move in moves
        ]
        
        # Trie par score décroissant
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        
        return scored_moves[:limit]

    def undo_last_move(self) -> Optional[Tuple[Move, int]]:
        """Annule le dernier coup joué."""
        return self.board.undo_last_move()

    def get_game_state(self) -> dict:
        """Retourne l'état actuel du jeu."""
        return {
            'board': str(self.board),
            'total_score': self.board.get_total_score(),
            'move_history': self.board.get_move_history()
        }
