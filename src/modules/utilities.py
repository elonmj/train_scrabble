from typing import Dict, List, Set, Tuple, Optional
from ..models.board import Board
from ..models.types import Direction
from ..models.gaddag import GADDAG


def placer_mot(mot: str, pos: Tuple[int, int], direction: Direction, 
               grille: Board) -> bool:
    """
    Place un mot sur la grille.
    
    Args:
        mot: Mot à placer
        pos: Position (row, col)
        direction: Direction du placement
        grille: Plateau de jeu
        
    Returns:
        True si le placement a réussi
    """
    row, col = pos
    
    # Vérifier les limites
    if direction == Direction.HORIZONTAL:
        if col + len(mot) > grille.size:
            return False
    else:
        if row + len(mot) > grille.size:
            return False
            
    # Vérifier les cases
    for i, lettre in enumerate(mot):
        if direction == Direction.HORIZONTAL:
            if not grille.place_letter(row, col + i, lettre):
                return False
        else:
            if not grille.place_letter(row + i, col, lettre):
                return False
                
    return True

