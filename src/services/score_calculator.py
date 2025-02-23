from typing import List, Tuple, Dict
from ..models.board import Board
from ..models.rack import Rack
from ..models.types import Direction, Move
from ..utils.board_utils import BoardUtils

class ScoreCalculator:
    """Gère le calcul des scores au Scrabble."""
    
    BINGO_BONUS = 50  # Bonus pour utilisation des 7 lettres
    
    # Valeurs des lettres
    LETTER_VALUES: Dict[str, int] = {
        'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
        'J': 8, 'K': 10, 'L': 1, 'M': 2, 'N': 1, 'O': 1, 'P': 3, 'Q': 8, 'R': 1,
        'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 10, 'X': 10, 'Y': 10, 'Z': 10
    }
    
    def __init__(self, board: Board):
        self.board = board
        self.board_utils = BoardUtils()

    def simulate_move_score(self, move: Move) -> int:
        """Simule le score d'un coup sans l'appliquer."""
        temp_multipliers = self.board.used_multipliers.copy()
        temp_grid = self.board.grid.copy()  # Add this
        try:
            return self.calculate_move_score(move, simulate=True)
        finally:
            self.board.used_multipliers = temp_multipliers
            self.board.grid = temp_grid  # Add this

    def calculate_move_score(self, move: Move, simulate: bool = False) -> int:
        """Calcule le score d'un coup SANS l'appliquer."""
        # Calcul du score principal
        word_score = self._calculate_word_score(move.word, move.row, move.col, move.direction)
        
        # Calcul des mots croisés
        cross_score = self._calculate_crossing_words_score(move)
        
        # Bonus bingo
        total_score = word_score + cross_score
        if len(move.word) == 7:
            total_score += self.BINGO_BONUS
            
        return total_score

    def _calculate_word_score(self, word: str, row: int, col: int, direction: Direction) -> int:
        """Calculate score for a single word."""
        print(f"\nCalcul score pour '{word}':")
        letter_score = 0
        word_multiplier = 1
        
        for i, letter in enumerate(word):
            current_row = row + (i if direction == Direction.VERTICAL else 0)
            current_col = col + (i if direction == Direction.HORIZONTAL else 0)
            
            if not self.board.get_letter(current_row, current_col):
                letter_mult, word_mult = self.board.get_square_multipliers(current_row, current_col)
                letter_value = self.LETTER_VALUES[letter]
                letter_points = letter_value * letter_mult
                letter_score += letter_points
                word_multiplier *= word_mult
                print(f"  Lettre '{letter}' ({letter_value}) en ({current_row},{current_col}): {letter_points} points (x{letter_mult} lettre, x{word_mult} mot)")
                self.board.use_multiplier(current_row, current_col)
            else:
                letter_value = self.LETTER_VALUES[letter]
                letter_score += letter_value
                print(f"  Lettre existante '{letter}' ({letter_value}) en ({current_row},{current_col})")
        
        final_score = letter_score * word_multiplier
        print(f"  Score final pour '{word}': {letter_score} x {word_multiplier} = {final_score}")
        return final_score

    def _calculate_crossing_words_score(self, move: Move) -> int:
        """Calcule le score total des mots croisés pour un coup."""
        print(f"\nCalcul des mots croisés pour {move.word}:")
        
        # Place the letters temporarily
        temp_grid = self.board.grid.copy()
        for i, letter in enumerate(move.word):
            current_row = move.row + (i if move.direction == Direction.VERTICAL else 0)
            current_col = move.col + (i if move.direction == Direction.HORIZONTAL else 0)
            self.board.grid[(current_row, current_col)] = letter

        try:
            cross_score = 0
            for i, letter in enumerate(move.word):
                current_row = move.row + (i if move.direction == Direction.VERTICAL else 0)
                current_col = move.col + (i if move.direction == Direction.HORIZONTAL else 0)
                
                if not temp_grid.get((current_row, current_col)):  # Vérifier avec temp_grid
                    cross_direction = Direction.VERTICAL if move.direction == Direction.HORIZONTAL else Direction.HORIZONTAL
                    
                    prefix = self.board_utils.get_prefix(self.board, current_row, current_col, cross_direction)
                    suffix = self.board_utils.get_suffix(self.board, current_row, current_col, cross_direction)
                    
                    if prefix or suffix:
                        cross_word = prefix + letter + suffix
                        start_row = current_row - len(prefix) if cross_direction == Direction.VERTICAL else current_row
                        start_col = current_col - len(prefix) if cross_direction == Direction.HORIZONTAL else current_col
                        print(f"  Mot croisé trouvé: '{cross_word}' à ({start_row},{start_col})")
                        
                        word_score = self._calculate_word_score(cross_word, start_row, start_col, cross_direction)
                        cross_score += word_score
                        print(f"  Score du mot croisé '{cross_word}': {word_score}")
            
            print(f"Score total des mots croisés: {cross_score}")
            return cross_score
        finally:
            self.board.grid = temp_grid
