from typing import Dict, List, Set, Tuple, Optional
from itertools import cycle
import random

# Assuming these are defined in external modules
from src.models.board import Board
from src.models.types import Direction, Move
from src.models.gaddag import GADDAG
from src.models.graph import ScrabbleGraph

# Adjusted constants
PARALLEL_MIN_DISTANCE = 2
PERPENDICULAR_MIN_DISTANCE = 1
MAX_TENTATIVES = 1000
GRID_SIZE = 15
CENTER = (7, 7)

directions = cycle([Direction.HORIZONTAL, Direction.VERTICAL] if random.random() < 0.5 else [Direction.VERTICAL, Direction.HORIZONTAL])
ZONES = [
    ((0, 6), (0, 6)),     # Upper-left
    ((0, 6), (8, 14)),    # Upper-right
    ((8, 14), (0, 6)),    # Lower-left
    ((8, 14), (8, 14))    # Lower-right
]


def placer_mot_central(grille: Board, dico: Set[str], lettres_appui: Dict[str, Dict[str, int]],
                      graphe: ScrabbleGraph) -> Optional[Tuple[str, int, int]]:
    """Place DATAIS vertically at the center of the grid (7,7)."""
    mot_centre = "DATAIS"
    direction = Direction.VERTICAL
    len_mot = len(mot_centre)

    x, y = CENTER[0] - 2, CENTER[1]  # (5, 7) for 'T' at (7,7)
    print(f"Placing {mot_centre} vertically at ({x}, {y})")
    for j, lettre in enumerate(mot_centre):
        grille.place_letter(x + j, y, lettre)

    graphe.add_word(mot_centre, (x, y), direction)
    graphe.central_word = mot_centre
    graphe.update_from_board(grille, {mot_centre}, lettres_appui)

    return mot_centre, x, y


def placer_mots_a_reviser(grille: Board, mots: List[str], dico: Set[str],
                         lettres_appui: Dict[str, Dict[str, int]], d_max: int,
                         sac_lettres: Dict[str, int], graphe: ScrabbleGraph,
                         max_tentatives: int = MAX_TENTATIVES) -> Tuple[Set[str], Set[str]]:
    """Place the words to revise in an isolated manner with spacing verification."""
    print(f"placer_mots_a_reviser called with mots={mots}, lettres_appui={lettres_appui}")
    mots_places = set()
    mots_non_places = set()
    placed_words_info = [("DATAIS", (5, 7), Direction.VERTICAL)]
    zone_cycle = cycle(ZONES)

    mots_sorted = sorted(mots, key=len, reverse=True)
    for mot in mots_sorted:
        print(f"Attempting placement for {mot}")
        place = False
        direction = next(directions)
        zone = next(zone_cycle)

        for dir_attempt in [direction, Direction.HORIZONTAL if direction == Direction.VERTICAL else Direction.VERTICAL]:
            (row_min, row_max), (col_min, col_max) = zone
            for tentative in range(max_tentatives // 2):
                max_row = min(row_max, GRID_SIZE - (len(mot) if dir_attempt == Direction.VERTICAL else 1))
                max_col = min(col_max, GRID_SIZE - (len(mot) if dir_attempt == Direction.HORIZONTAL else 1))
                if max_row < row_min or max_col < col_min:
                    print(f"  No valid positions in zone {zone} for {mot} in {dir_attempt}")
                    continue

                row = random.randint(row_min, max_row)
                col = random.randint(col_min, max_col)

                if est_position_valide(mot, row, col, dir_attempt, grille, dico, placed_words_info=placed_words_info):
                    for i, lettre in enumerate(mot):
                        if dir_attempt == Direction.HORIZONTAL:
                            grille.place_letter(row, col + i, lettre)
                        else:
                            grille.place_letter(row + i, col, lettre)
                    graphe.add_word(mot, (row, col), dir_attempt)
                    mots_places.add(mot)
                    placed_words_info.append((mot, (row, col), dir_attempt))
                    all_placed = mots_places | {"DATAIS"}
                    graphe.update_from_board(grille, all_placed, lettres_appui)
                    print(f"Successfully placed {mot} at ({row}, {col}) in direction {dir_attempt} (zone: {zone})")
                    place = True
                    break

            if place:
                break

        if not place:
            print(f"Impossible de placer le mot {mot} après {max_tentatives} tentatives")
            mots_non_places.add(mot)

    if mots_places:
        verifier_isolation_et_clarte(grille, placed_words_info)

    return mots_places, mots_non_places


def est_position_valide(mot: str, row: int, col: int, direction: Direction,
                        grille: Board, dico: Set[str],
                        placed_words_info: Optional[List[Tuple[str, Tuple[int, int], Direction]]] = None) -> bool:
    """Check the validity of placement for isolated words with reduced spacing."""
    print(f"Checking {mot} at ({row}, {col}), dir={direction}")
    
    # Boundary check
    if row < 0 or col < 0 or (direction == Direction.HORIZONTAL and col + len(mot) > GRID_SIZE) or \
       (direction == Direction.VERTICAL and row + len(mot) > GRID_SIZE):
        print(f"  Rejected: Out of bounds")
        return False

    # Overlap check
    new_positions = [(row + i if direction == Direction.VERTICAL else row,
                      col + i if direction == Direction.HORIZONTAL else col) for i in range(len(mot))]
    for r, c in new_positions:
        if grille.get_letter(r, c):
            print(f"  Rejected: Overlap conflict at ({r}, {c})")
            return False

    # Spacing check with previously placed words
    if placed_words_info:
        for placed_word, (pr, pc), placed_dir in placed_words_info:
            placed_positions = [(pr + j if placed_dir == Direction.VERTICAL else pr,
                                 pc + j if placed_dir == Direction.HORIZONTAL else pc) for j in range(len(placed_word))]

            if direction == placed_dir:  # Parallel check
                if direction == Direction.VERTICAL:
                    distance = abs(col - pc)
                    new_range = (row, row + len(mot) - 1)
                    placed_range = (pr, pr + len(placed_word) - 1)
                    overlap = max(new_range[0], placed_range[0]) <= min(new_range[1], placed_range[1])
                    if distance < PARALLEL_MIN_DISTANCE and overlap:
                        print(f"  Rejected: Parallel spacing conflict with {placed_word}: distance={distance}, overlap={overlap}")
                        return False
                else:  # HORIZONTAL
                    distance = abs(row - pr)
                    new_range = (col, col + len(mot) - 1)
                    placed_range = (pc, pc + len(placed_word) - 1)
                    overlap = max(new_range[0], placed_range[0]) <= min(new_range[1], placed_range[1])
                    if distance < PARALLEL_MIN_DISTANCE and overlap:
                        print(f"  Rejected: Parallel spacing conflict with {placed_word}: distance={distance}, overlap={overlap}")
                        return False
            # Perpendicular check
            for r, c in new_positions:
                for pr_j, pc_j in placed_positions:
                    distance = abs(r - pr_j) + abs(c - pc_j)
                    if distance < PERPENDICULAR_MIN_DISTANCE:
                        print(f"  Rejected: Perpendicular spacing conflict with {placed_word} at ({r}, {c}) - distance={distance}")
                        return False

    print(f"  Accepted: Position is valid")
    return True


def verifier_isolation_et_clarte(grille: Board, placed_words_info: List[Tuple[str, Tuple[int, int], Direction]]) -> None:
    """Verify isolation and measure grid clarity."""
    print("\n=== Vérification de l’isolation et de la clarté ===")
    
    all_positions = {}
    for word, (row, col), direction in placed_words_info:
        positions = [(row + i if direction == Direction.VERTICAL else row,
                      col + i if direction == Direction.HORIZONTAL else col) for i in range(len(word))]
        all_positions[word] = positions

    for word1, pos1 in all_positions.items():
        for word2, pos2 in all_positions.items():
            if word1 == word2:
                continue
            for r1, c1 in pos1:
                for r2, c2 in pos2:
                    distance = abs(r1 - r2) + abs(c1 - c2)
                    if distance < 2:
                        print(f"Erreur : {word1} et {word2} sont trop proches ou adjacents à ({r1}, {c1}) et ({r2}, {c2})")
                        return

    print("Tous les mots sont isolés (distance minimale ≥ 2).")

    distances = []
    for i, (word1, pos1) in enumerate(all_positions.items()):
        for word2, pos2 in list(all_positions.items())[i+1:]:
            min_dist = float('inf')
            for r1, c1 in pos1:
                for r2, c2 in pos2:
                    dist = abs(r1 - r2) + abs(c1 - c2)
                    min_dist = min(min_dist, dist)
            distances.append(min_dist)
            print(f"Distance minimale entre {word1} et {word2} : {min_dist}")

    if distances:
        avg_distance = sum(distances) / len(distances)
        print(f"Distance moyenne entre les mots : {avg_distance:.2f}")
        if avg_distance >= 5:
            print("Clarté de la grille : Élevée (bonne répartition)")
        elif avg_distance >= 3:
            print("Clarté de la grille : Moyenne (acceptable)")
        else:
            print("Clarté de la grille : Faible (trop serré)")
    else:
        print("Pas assez de mots pour mesurer la clarté.")


if __name__ == "__main__":
    grille = Board()
    dico = {"DATAIS", "BACCARAT", "CACABERA", "BACCARAS"}
    lettres_appui = {
        "CACABERA": {"E": 6},
        "BACCARAS": {"S": 7},
        "BACCARAT": {"T": 7}
    }
    graphe = ScrabbleGraph()
    sac_lettres = {}

    placer_mot_central(grille, dico, lettres_appui, graphe)
    grille.debug_print("Après placement du mot central")
    mots_a_reviser = ["BACCARAT", "CACABERA", "BACCARAS"]
    placer_mots_a_reviser(grille, mots_a_reviser, dico, lettres_appui, 5, sac_lettres, graphe)
    grille.debug_print("Après placement des mots à réviser")