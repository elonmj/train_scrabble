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



def trouver_position(mot: str, grille: Board) -> Optional[Tuple[int, int]]:
    """
    Trouve la position d'un mot sur la grille.
    
    Args:
        mot: Mot à trouver
        grille: Plateau de jeu
        
    Returns:
        Tuple (row, col) si trouvé, None sinon
    """
    for row in range(grille.size):
        for col in range(grille.size):
            if grille.get_letter(row, col) == mot[0]:
                # Vérifie horizontalement
                if all(col + i < grille.size and grille.get_letter(row, col + i) == mot[i] 
                      for i in range(len(mot))):
                    return row, col
                # Vérifie verticalement
                if all(row + i < grille.size and grille.get_letter(row + i, col) == mot[i] 
                      for i in range(len(mot))):
                    return row, col
    return None

def trouver_orientation(mot: str, grille: Board) -> Optional[Direction]:
    """
    Trouve l'orientation d'un mot sur la grille.
    
    Args:
        mot: Mot à trouver
        grille: Plateau de jeu
        
    Returns:
        Direction du mot si trouvé, None sinon
    """
    pos = trouver_position(mot, grille)
    if not pos:
        return None
        
    row, col = pos
    # Vérifie horizontalement
    if all(col + i < grille.size and grille.get_letter(row, col + i) == mot[i] 
          for i in range(len(mot))):
        return Direction.HORIZONTAL
    # Vérifie verticalement
    if all(row + i < grille.size and grille.get_letter(row + i, col) == mot[i] 
          for i in range(len(mot))):
        return Direction.VERTICAL
    return None

def trouver_mots_courts_valides(dico: Set[str], gaddag: GADDAG, longueur_max: int = 5) -> List[str]:
    """
    Trouve tous les mots valides du dictionnaire ayant une longueur inférieure ou égale à longueur_max.
    
    Args:
        dico: Dictionnaire des mots valides
        gaddag: Structure GADDAG pour la validation des mots
        longueur_max: Longueur maximale des mots à retourner
        
    Returns:
        Liste des mots courts valides
    """
    mots_courts = []
    for mot in dico:
        if len(mot) <= longueur_max and gaddag.is_word(mot):
            mots_courts.append(mot)
    return mots_courts

