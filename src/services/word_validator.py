from typing import List, Set, Tuple
from ..models.board import Board
from ..models.gaddag import GADDAG
from ..models.types import Direction
from ..utils.board_utils import BoardUtils

class WordValidator:
    """Valide les mots et les coups au Scrabble."""
    
    def __init__(self, board: Board, gaddag: GADDAG):
        self.board = board
        self.gaddag = gaddag
        self.board_utils = BoardUtils()
        
    def is_valid_word(self, word: str) -> bool:
        """Vérifie si un mot existe dans le dictionnaire."""
        return self.gaddag.contains(word)
        
    def is_valid_move(self, word: str, row: int, col: int, direction: Direction, graphe) -> bool:
        """
        Vérifie si un coup est valide localement (sans vérifier la connectivité globale).
        Vérifie uniquement :
        1. Si le mot existe dans le dictionnaire
        2. Si le placement est possible physiquement (limites, chevauchements)
        3. Si les mots croisés formés sont valides
        """
        # 1. Vérifie le mot principal
        if not self.is_valid_word(word):
            return False
            
        # 2. Vérifie les limites et chevauchements
        if direction == Direction.HORIZONTAL:
            if col + len(word) > self.board.size:
                return False
        else:
            if row + len(word) > self.board.size:
                return False
                
        # Vérifie les chevauchements
        for i in range(len(word)):
            curr_row = row + (i if direction == Direction.VERTICAL else 0)
            curr_col = col + (i if direction == Direction.HORIZONTAL else 0)
            
            existing = self.board.get_letter(curr_row, curr_col)
            if existing and existing != word[i]:
                return False
        
        # 3. Vérifie les mots croisés formés
        for i, letter in enumerate(word):
            current_row = row + (i if direction == Direction.VERTICAL else 0)
            current_col = col + (i if direction == Direction.HORIZONTAL else 0)
            
            if not self.board.get_letter(current_row, current_col):
                if not self._is_valid_cross_word(current_row, current_col, direction, letter, graphe):
                    return False

        return True
        
    def _is_valid_cross_word(self, row: int, col: int, main_direction: Direction, letter: str, graphe) -> bool:
        """Vérifie si le placement d'une lettre forme des mots croisés valides."""
        cross_direction = Direction.VERTICAL if main_direction == Direction.HORIZONTAL else Direction.HORIZONTAL
        
        prefix = self.board_utils.get_prefix(self.board, row, col, cross_direction)
        suffix = self.board_utils.get_suffix(self.board, row, col, cross_direction)
        
        if not prefix and not suffix:
            return True
        
        cross_word = prefix + letter + suffix
        
        # Skip check if adjacent cell is part of an existing word
        if graphe.is_cell_occupied(row, col):
            return True

        return self.is_valid_word(cross_word)

    # Remove _is_valid_placement and _get_adjacent_cells as they're now handled by BoardUtils
