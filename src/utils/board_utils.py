from typing import List, Set
from ..models.board import Board
from ..models.types import Direction
from typing import List, Set, Tuple, Optional

class BoardUtils:
    """Utilitaires pour manipuler le plateau de jeu."""
    
    @staticmethod
    def get_prefix(board: Board, row: int, col: int, direction: Direction) -> str:
        """Obtient le préfixe pour une position donnée."""
        prefix = []
        current_row, current_col = row, col
        
        while True:
            if direction == Direction.HORIZONTAL:
                current_col -= 1
            else:
                current_row -= 1
                
            if not (0 <= current_row < board.size and 
                   0 <= current_col < board.size):
                break
                
            letter = board.get_letter(current_row, current_col)
            if not letter:
                break
            prefix.insert(0, letter)
            
        return ''.join(prefix)
    
    @staticmethod
    def get_suffix(board: Board, row: int, col: int, direction: Direction) -> str:
        """Obtient le suffixe pour une position donnée."""
        suffix = []
        current_row, current_col = row, col
        
        while True:
            if direction == Direction.HORIZONTAL:
                current_col += 1
            else:
                current_row += 1
                
            if not (0 <= current_row < board.size and 
                   0 <= current_col < board.size):
                break
                
            letter = board.get_letter(current_row, current_col)
            if not letter:
                break
            suffix.append(letter)
            
        return ''.join(suffix)
    
    def check_word_placement(self, board: Board, word: str, row: int, col: int, direction: Direction) -> bool:
        """Vérifie les règles de base pour le placement d'un mot."""
        print(f"\n  Check placement de '{word}' en ({row},{col}) {direction}")
        
        # 1. Vérifie les limites du plateau
        word_length = len(word)
        if direction == Direction.HORIZONTAL:
            if col < 0 or col + word_length > board.size:
                print("  ❌ Dépasse les limites horizontales")
                return False
        else:  # VERTICAL
            if row < 0 or row + word_length > board.size:
                print("  ❌ Dépasse les limites verticales")
                return False
        print("  ✅ Dans les limites du plateau")

        # 2. Vérifie le premier coup
        if len(board.grid) == 0:
            center = board.size // 2
            if direction == Direction.HORIZONTAL:
                valid = row == center and (col <= center < col + word_length)
            else:  # VERTICAL
                valid = col == center and (row <= center < row + word_length)
            print(f"  {'✅' if valid else '❌'} Premier coup (doit passer par le centre)")
            return valid

        # 3. Vérifie les connexions
        found_anchor = False
        found_connection = False
        
        print("  Vérification des connexions:")
        for i, letter in enumerate(word):
            current_row = row + (i if direction == Direction.VERTICAL else 0)
            current_col = col + (i if direction == Direction.HORIZONTAL else 0)
            
            existing = board.get_letter(current_row, current_col)
            if existing:
                if existing != letter:
                    print(f"  ❌ Conflit de lettre en ({current_row},{current_col}): {existing} ≠ {letter}")
                    return False
                print(f"  ✅ Lettre existante '{existing}' en ({current_row},{current_col})")
                found_anchor = True
                found_connection = True
            elif board.is_adjacent_to_letter(current_row, current_col):
                print(f"  ✅ Connexion adjacente trouvée en ({current_row},{current_col})")
                found_connection = True

        valid = found_connection or (len(board.grid) == 0 and word_length > 0)
        print(f"  {'✅' if valid else '❌'} Résultat final du placement")
        return valid

