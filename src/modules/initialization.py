from typing import Dict, List, Set, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from itertools import cycle
import random
from src.models import graph
from ..models.board import Board
from ..models.types import Direction, Move
from ..models.gaddag import GADDAG
from ..models.graph import ScrabbleGraph

class ConnectionPoint(NamedTuple):
    """Represents a potential connection point on the board."""
    position: Tuple[int, int]
    letter: str
    direction: Direction

def placer_mot_central(grille: Board, dico: Set[str], lettres_appui: Dict[str, Dict[str, int]],
                       graphe: ScrabbleGraph) -> Optional[Tuple[str, int, int]]:
    """Place le mot central sur la grille en passant par la case centrale."""
    mots_valides = [mot for mot in dico if 4 <= len(mot) <= 7]
    if not mots_valides:
        return None

    mot_centre = random.choice(mots_valides)
    direction = Direction.VERTICAL  # Force vertical placement for the central word

    pos_centrale = grille.center
    len_mot = len(mot_centre)
    i = random.randint(0, len_mot - 1)  # Position de la lettre sur le centre

    x = pos_centrale - i
    y = pos_centrale

    print(f"Placing {mot_centre} with letter {mot_centre[i]} at center ({direction})")
    for j, lettre in enumerate(mot_centre):
        grille.place_letter(x + j, y, lettre)

    graphe.add_word(mot_centre, (x, y), direction)
    graphe.central_word = mot_centre
    graphe.update_from_board(grille, {mot_centre}, lettres_appui)

    return mot_centre, x, y




def placer_mots_a_reviser(grille: Board, mots: List[str], dico: Set[str],
                        lettres_appui: Dict[str, Dict[str, int]], d_max: int,
                        sac_lettres: Dict[str, int], graphe: ScrabbleGraph,
                        max_tentatives: int = 100) -> Tuple[Set[str], Set[str]]:
    """
    Place les mots à réviser sur la grille en respectant leurs lettres d'appui.
    Version améliorée avec meilleure gestion des directions et connexions.
    """
    print(f"placer_mots_a_reviser called with mots={mots}, lettres_appui={lettres_appui}")
    mots_places = set()
    mots_non_places = set()

    # Use itertools.cycle to alternate between horizontal and vertical for words without constraints
    directions = cycle([Direction.HORIZONTAL, Direction.VERTICAL])

    # 1. Trier les mots par priorité de connexion
    mots_tries = sorted(mots, key=lambda m: len(lettres_appui.get(m, {})), reverse=True)
    print(f"mots_tries={mots_tries}")

    # 2. Obtenir les informations du mot central
    mot_central = graphe.central_word
    if mot_central in graphe.nodes:
        node_central = graphe.nodes[mot_central]
        pos_centrale = node_central.position
        dir_centrale = node_central.direction

        # 3. Trouver les points de connexion pour chaque mot
        points_connexion = trouver_points_connexion(
            mot_central, pos_centrale, dir_centrale, lettres_appui, board_size=grille.size
        )

        # 4. Placer les mots en utilisant les points de connexion
        for mot in mots_tries:
            place = False
            if mot in points_connexion:  # Check if we have connection points
                # Try each connection point
                for point in points_connexion[mot]:
                    # Get the required index for this letter from lettres_appui
                    required_idx = lettres_appui[mot][point.letter]
                    # Check if the required index is valid and the word has the correct letter at that index
                    if required_idx >= 0 and required_idx < len(mot) and mot[required_idx] == point.letter:
                        pos_debut = calculer_position_mot(mot, point, required_idx)
                        print(f"Trying to connect {mot} at {pos_debut} using letter {point.letter} (required index {required_idx})")

                        # Try the word's direction
                        if est_position_valide(mot, pos_debut[0], pos_debut[1],
                                           point.direction, grille, dico,
                                           required_connection=point.position):
                            # Placer le mot
                            for j, l in enumerate(mot):
                                if point.direction == Direction.HORIZONTAL:
                                    grille.place_letter(pos_debut[0], pos_debut[1] + j, l)
                                else:
                                    grille.place_letter(pos_debut[0] + j, pos_debut[1], l)

                            # Add word to graph and update places without resetting previous placements
                            graphe.add_word(mot, pos_debut, point.direction)
                            mots_places.add(mot)
                            # Update graph with accumulated words
                            all_placed = mots_places | {mot}
                            graphe.update_from_board(grille, all_placed, lettres_appui)
                            # Print debug info
                            print(f"Successfully placed {mot} at {pos_debut} in direction {point.direction}")
                            place = True
                            break

            # Try random placement if word has no required connection points
            if not place and mot not in lettres_appui:
                print(f"Attempting random placement for {mot} (no connection requirements)")
                # Get the next direction from our alternating cycle
                direction = next(directions)
                
                # Try both directions if first one fails
                for dir_attempt in [direction, Direction.HORIZONTAL if direction == Direction.VERTICAL else Direction.VERTICAL]:
                    for tentative in range(max_tentatives // 2):  # Split attempts between directions
                        # Calculate valid boundaries
                        max_row = grille.size - (len(mot) if dir_attempt == Direction.VERTICAL else 1)
                        max_col = grille.size - (len(mot) if dir_attempt == Direction.HORIZONTAL else 1)

                        if max_row < 0 or max_col < 0:  # Skip if word is too long for this direction
                            continue

                        # Try a random position
                        row = random.randint(0, max_row)
                        col = random.randint(0, max_col)

                        if est_position_valide(mot, row, col, dir_attempt, grille, dico):
                            # Place the word
                            for i, lettre in enumerate(mot):
                                if dir_attempt == Direction.HORIZONTAL:
                                    grille.place_letter(row, col + i, lettre)
                                else:
                                    grille.place_letter(row + i, col, lettre)

                            # Add word to graph and update places
                            graphe.add_word(mot, (row, col), dir_attempt)
                            mots_places.add(mot)
                            # Update graph with accumulated words
                            all_placed = mots_places | {mot}
                            graphe.update_from_board(grille, all_placed, lettres_appui)
                            # Print debug info
                            print(f"Successfully placed {mot} at {(row, col)} in direction {dir_attempt} (random placement)")
                            place = True
                            break
                    
                    if place:  # If placed successfully in this direction, stop trying
                        break

            if not place:
                print(f"Impossible de placer le mot {mot}")
                mots_non_places.add(mot)

    return mots_places, mots_non_places

def est_position_valide(mot: str, row: int, col: int, direction: Direction,
                          grille: Board, dico: Set[str],
                          required_connection: Optional[Tuple[int, int]] = None,
                          skip_adjacent: Optional[Set[Tuple[int,int]]] = None) -> bool:
    """
    Vérifie si une position est valide pour placer un mot.
    Validation simplifiée : uniquement les limites du plateau et les chevauchements.
    
    Args:
        required_connection: Position spécifique où le mot doit se connecter
    """
    print(f"est_position_valide: mot={mot}, pos=({row}, {col}), dir={direction}, required_connection={required_connection}") # DEBUG
    # Check boundaries
    if row < 0 or col < 0:
        print(f"   boundaries failed: row={row}, col={col}") # DEBUG
        print(f"est_position_valide returns False (boundaries)") # DEBUG
        return False
    if direction == Direction.HORIZONTAL:
        if col + len(mot) > grille.size:
            print(f"  boundaries failed: col + len(mot) = {col + len(mot)}, grille.size = {grille.size}") # DEBUG
            print(f"est_position_valide returns False (boundaries - horizontal)") # DEBUG
            return False
    else:
        if row + len(mot) > grille.size:
            print(f"  boundaries failed: row + len(mot) = {row + len(mot)}, grille.size = {grille.size}") # DEBUG
            print(f"est_position_valide returns False (boundaries - vertical)") # DEBUG
            return False

    # Initialize required connection tracking
    required_connection_found = required_connection is None

    # Check each position along the word
    for i in range(len(mot)):
        r = row + (i if direction == Direction.VERTICAL else 0)
        c = col + (i if direction == Direction.HORIZONTAL else 0)
        
        # Check letter conflicts
        existing = grille.get_letter(r, c)
        if existing and existing != mot[i]:
            print(f"  letter conflict at ({r}, {c}): existing={existing}, new={mot[i]}") # DEBUG
            print(f"est_position_valide returns False (letter conflict)") # DEBUG
            return False
        
        # Check required connection point
        if required_connection and (r, c) == required_connection:
            if mot[i] == grille.get_letter(r, c):
                required_connection_found = True
            else:
                print(f"  required connection failed at ({r}, {c}): word_letter={mot[i]}, board_letter={grille.get_letter(r, c)}") # DEBUG
                print(f"est_position_valide returns False (required connection)") # DEBUG
                return False

    print(f"est_position_valide returns {required_connection_found}") # DEBUG
    return required_connection_found
