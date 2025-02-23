import string
from typing import Dict, List, Set, Tuple, Optional

from ..models.types import Direction, Move
from .score_calculator import ScoreCalculator
from .word_validator import WordValidator
from ..models.node import Node
from ..models.gaddag import GADDAG
from ..models.board import Board
from ..models.rack import Rack
from ..utils.board_utils import BoardUtils

class MoveGenerator:
    """Générateur de coups possibles pour le Scrabble."""
    
    def __init__(self, gaddag: GADDAG, board: Board):
        self.gaddag = gaddag
        self.board = board
        self.validator = WordValidator(board, gaddag)
        self.score_calculator = ScoreCalculator(board)
        self.board_utils = BoardUtils()
        self._blank_letter = '_'  # Ajouter cette constante

    def generate_moves(self, rack_str: str) -> List[Move]:  # Fix syntax error in type hint
        """Génère tous les coups possibles pour un rack donné."""
        moves: List[Move] = []
        rack = Rack(rack_str)
        
        # Analyse le plateau pour trouver les contraintes
        constraints = self._analyze_board()
        
        # Pour chaque point d'ancrage
        for (row, col), directions in constraints.items():
            # Pour chaque direction possible
            for direction, valid_letters in directions.items():
                dir_enum = Direction(direction)
                
                # Définit le contexte de recherche
                prefix = self._get_prefix(row, col, dir_enum)
                suffix = self._get_suffix(row, col, dir_enum)
                
                # Si on a un préfixe, vérifie s'il existe dans le GADDAG
                if prefix:
                    node = self.gaddag.root
                    reversed_prefix = prefix[::-1]  # Il faut inverser le préfixe !
                    for char in reversed_prefix:
                        if not node.has_transition(char):
                            break  # On devrait break ici, pas continue
                        node = node.get_transition(char)
                        
                # Trouve les lettres possibles à cette position
                available_letters = rack.get_possible_letters()
                if valid_letters:
                    available_letters &= valid_letters
                
                # Pour chaque lettre possible
                for letter in available_letters:
                    temp_rack = Rack(rack_str)
                    temp_rack.remove_letters(letter)
                    
                    # Cherche les mots possibles avec cette lettre
                    words = self._find_words(row, col, dir_enum, letter, temp_rack)
                    
                    # Ajoute les mouvements trouvés
                    for word in words:
                        # Calcule la position de départ du mot
                        start_row = row
                        start_col = col
                        if dir_enum == Direction.HORIZONTAL:
                            start_col -= len(prefix)
                        else:
                            start_row -= len(prefix)
                            
                        moves.append(Move(
                            word=word,
                            row=start_row,
                            col=start_col,
                            direction=dir_enum,
                            score=self.score_calculator.calculate_move_score(Move(
                                word=word,
                                row=start_row,
                                col=start_col,
                                direction=dir_enum
                            ))
                        ))
        
        return moves

    def _analyze_board(self) -> Dict[Tuple[int, int], Dict[str, Set[str]]]:
        """Analyse le plateau pour trouver les points d'ancrage et leurs contraintes."""
        constraints: Dict[Tuple[int, int], Dict[str, Set[str]]] = {}
        
        def add_constraint(row: int, col: int, direction: str, letters: Set[str]) -> None:
            pos = (row, col)
            if pos not in constraints:
                constraints[pos] = {}
            constraints[pos][direction] = letters

        # On ne doit analyser que les points d'ancrage non-internes
        for row in range(self.board.size):
            for col in range(self.board.size):
                if not self.board.get_letter(row, col) and not self._is_internal_anchor(row, col):
                    adjacent = False
                    
                    for d in Direction:
                        # Vérifie si il y a des lettres adjacentes dans la direction opposée
                        if d == Direction.HORIZONTAL:
                            has_cross = (row > 0 and self.board.get_letter(row-1, col)) or \
                                      (row < self.board.size-1 and self.board.get_letter(row+1, col))
                        else:
                            has_cross = (col > 0 and self.board.get_letter(row, col-1)) or \
                                       (col < self.board.size-1 and self.board.get_letter(row, col+1))
                        
                        if has_cross:
                            adjacent = True
                            valid_letters = self._get_valid_letters(row, col, d)
                            if valid_letters:
                                add_constraint(row, col, d.value, valid_letters)
                    
                    if adjacent:
                        for d in Direction:
                            if d.value not in constraints.get((row, col), {}):
                                add_constraint(row, col, d.value, set(string.ascii_uppercase))
        
        return constraints

    def _get_valid_letters(self, row: int, col: int, direction: Direction) -> Set[str]:
        """Détermine les lettres valides pour une position donnée."""
        # Commence avec toutes les lettres possibles
        valid_letters = set(string.ascii_uppercase)
        
        # Obtient le préfixe et le suffixe
        prefix = self._get_prefix(row, col, direction)
        suffix = self._get_suffix(row, col, direction)
        
        if prefix or suffix:
            node = self.gaddag.root
            
            # Navigue jusqu'au nœud approprié
            if prefix:
                reversed_prefix = prefix[::-1]
                for char in reversed_prefix:
                    if not node.has_transition(char):
                        return set()
                    node = node.get_transition(char)
                    
            # Ajoute le délimiteur
            if not node.has_transition(self.gaddag.DELIMITER):
                return set()
            node = node.get_transition(self.gaddag.DELIMITER)
            
            # Vérifie le suffixe
            if suffix:
                temp_node = node
                for char in suffix:
                    if not temp_node.has_transition(char):
                        return set()
                    temp_node = temp_node.get_transition(char)
            
            # Retourne les lettres valides à cette position
            return set(node.transitions.keys())
            
        return valid_letters

    def _get_prefix(self, row: int, col: int, direction: Direction) -> str:
        return self.board_utils.get_prefix(self.board, row, col, direction)

    def _get_suffix(self, row: int, col: int, direction: Direction) -> str:
        return self.board_utils.get_suffix(self.board, row, col, direction)

    def _is_internal_anchor(self, row: int, col: int) -> bool:
        """
        Vérifie si une position est un point d'ancrage interne dans une séquence continue.
        Selon l'algorithme GADDAG, on peut ignorer ces points pour optimiser la recherche.
        """
        # Vérifie horizontalement
        has_left = col > 0 and self.board.get_letter(row, col-1)
        has_right = col < self.board.size-1 and self.board.get_letter(row, col+1)
        if has_left and has_right:
            return True
            
        # Vérifie verticalement
        has_up = row > 0 and self.board.get_letter(row-1, col)
        has_down = row < self.board.size-1 and self.board.get_letter(row+1, col)
        return has_up and has_down

    def _find_words(self, row: int, col: int, direction: Direction, 
                   letter: str, rack: Rack) -> List[str]:
        """Trouve tous les mots possibles à partir d'une position et d'une lettre."""
        words: List[str] = []
        if self._is_internal_anchor(row, col):
            return words

        prefix = self._get_prefix(row, col, direction)
        current_node = self.gaddag.root

        # Navigation GADDAG
        if prefix:
            for char in prefix[::-1]:
                if not current_node.has_transition(char):
                    return words
                current_node = current_node.get_transition(char)

        if not current_node.has_transition(self.gaddag.DELIMITER):
            return words
        current_node = current_node.get_transition(self.gaddag.DELIMITER)

        def explore_suffixes(node: Node, used_letters: str, remaining_rack: Rack) -> None:
            if node.is_terminal:
                word = prefix + letter + used_letters
                # Utiliser directement le validateur pour tout vérifier
                if self.validator.is_valid_move(word, row, col, direction):
                    words.append(word)

            # Lettres normales
            for next_letter in remaining_rack.get_possible_letters():
                if next_letter != self._blank_letter and node.has_transition(next_letter):
                    temp_rack = Rack(str(remaining_rack))
                    if temp_rack.remove_letters(next_letter):
                        explore_suffixes(
                            node.get_transition(next_letter),
                            used_letters + next_letter,
                            temp_rack
                        )

            # Gestion des blanks
            if self._blank_letter in remaining_rack.get_possible_letters():
                temp_rack = Rack(str(remaining_rack))
                if temp_rack.remove_letters(self._blank_letter):
                    for blank_letter in string.ascii_uppercase:
                        if node.has_transition(blank_letter):
                            explore_suffixes(
                                node.get_transition(blank_letter),
                                used_letters + blank_letter.lower(),  # blank en minuscule
                                temp_rack
                            )

        # Premier appel avec la lettre d'ancrage
        if current_node.has_transition(letter):
            explore_suffixes(
                current_node.get_transition(letter),
                "",
                Rack(str(rack))
            )

        return words
