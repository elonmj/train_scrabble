from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from ..models.board import Board
from ..models.types import Direction
from ..models.gaddag import GADDAG
from ..models.graph import ScrabbleGraph, Connection

# Constants for geometric validation
D_MAX = 15  # Maximum board dimension
MIN_SEP = 2  # Min separation for parallel words

def calculate_separation(
    pos1: Tuple[int, int],
    dir1: Direction,
    len1: int,
    pos2: Tuple[int, int],
    dir2: Direction,
    len2: int
) -> Tuple[int, int]:
    """Calculates vertical/horizontal separation between words."""
    row1, col1 = pos1
    row2, col2 = pos2

    if dir1 == dir2 == Direction.HORIZONTAL:
        v_sep = abs(row2 - row1)
        # Calculate word start and end positions
        start1, end1 = col1, col1 + len1 - 1
        start2, end2 = col2, col2 + len2 - 1

        # Check for overlap
        if max(start1, start2) <= min(end1, end2):
            h_sep = 0  # Overlapping words
        else:
            h_sep = max(0, max(start1, start2) - min(end1, end2) -1)  # No negative gaps
        return v_sep, h_sep

    elif dir1 == dir2 == Direction.VERTICAL:
        h_sep = abs(col2 - col1)
        # Calculate word start and end positions
        start1, end1 = row1, row1 + len1 - 1
        start2, end2 = row2, row2 + len2 - 1

        # Check for overlap
        if max(start1, start2) <= min(end1, end2):
            v_sep = 0  # Overlapping words
        else:
            v_sep = max(0, max(start1, start2) - min(end1, end2) -1)  # No negative gaps

        return v_sep, h_sep
    else:
        return abs(row2 - row1), abs(col2 - col1)
    
def is_valid_word_placement(
    v_sep: int, h_sep: int, dir1: Direction, dir2: Direction, d_max: int
) -> bool:
    """Checks if word placement is geometrically valid."""
    if dir1 == dir2:
        if dir1 == Direction.HORIZONTAL and v_sep < MIN_SEP:
            return False
        if dir1 == Direction.VERTICAL and h_sep < MIN_SEP:
            return False
    return True

@dataclass(order=True)
class ConnectionCandidate:
    """Represents a potential connection, prioritized by score."""
    score: float
    word1: str
    word2: str
    bridge_word: str
    bridge_pos: Tuple[int, int]
    bridge_direction: Direction
    connection_details: Optional[List[Connection]] = None

def get_letter_position(pos: Tuple[int, int], index: int, direction: Direction) -> Tuple[int, int]:
    """Calculates the position of a letter within a word."""
    row, col = pos
    return (row, col + index) if direction == Direction.HORIZONTAL else (row + index, col)

def find_bridge_words(
    word1: str,
    pos1: Tuple[int, int],
    dir1: Direction,
    word2: str,
    pos2: Tuple[int, int],
    dir2: Direction,
    lettres_appui: Dict[str, Dict[str, int]],
    gaddag: GADDAG,
    lettres_disponibles: Dict[str, int]
) -> List[ConnectionCandidate]:
    """Finds potential bridge words using the GADDAG."""
    candidates: List[ConnectionCandidate] = []
    
    # Keep letter counts for validation
    available_letter_counts = {gaddag.normalize_word(l): count
                             for l, count in lettres_disponibles.items()}
    available_letters = set(available_letter_counts.keys())
    
    # Add support letters to available set
    if lettres_appui:
        for word_letters in lettres_appui.values():
            available_letters.update(gaddag.normalize_word(l) for l in word_letters.keys())

    # Determine bridge direction
    bridge_direction = Direction.VERTICAL if dir1 == Direction.HORIZONTAL else Direction.HORIZONTAL
    
    # Get available letters from both support letters and available letters
    letters1_to_check = lettres_appui.get(word1, {}) if lettres_appui else {}
    letters2_to_check = lettres_appui.get(word2, {}) if lettres_appui else {}
    
    # If no support letters, use all letters
    if not letters1_to_check:
        letters1_to_check = {letter: i for i, letter in enumerate(word1)}
    if not letters2_to_check:
        letters2_to_check = {letter: i for i, letter in enumerate(word2)}

    for letter1, i1 in letters1_to_check.items():
        pos1_letter = get_letter_position(pos1, i1, dir1)
        for letter2, i2 in letters2_to_check.items():
            pos2_letter = get_letter_position(pos2, i2, dir2)

            # Build skeleton and determine bridge position based on intersection points
            # For a valid bridge word, letters from both words must be on same line/column
            if bridge_direction == Direction.VERTICAL:
                if pos1_letter[1] != pos2_letter[1]:  # Must be in same column
                    continue
                row_dist = abs(pos1_letter[0] - pos2_letter[0])
                if row_dist <= 1 or row_dist > D_MAX:  # Must have space for a word
                    continue
                # Build skeleton with both required letters
                # Add one to skeleton positions to leave room for first letter
                first_pos = min(pos1_letter[0], pos2_letter[0])
                skeleton = {
                    (pos1_letter[0] - first_pos + 1): letter1.upper(),  # Add 1 to skeleton positions
                    (pos2_letter[0] - first_pos + 1): letter2.upper()   # Add 1 to skeleton positions
                }
                bridge_start_pos = (first_pos - 1, pos1_letter[1])  # Adjust start pos back by 1
            else:  # Horizontal bridge
                if pos1_letter[0] != pos2_letter[0]:  # Must be in same row
                    continue
                col_dist = abs(pos1_letter[1] - pos2_letter[1])
                if col_dist <= 1 or col_dist > D_MAX:
                    continue
                # Build skeleton for horizontal bridge
                min_col = min(pos1_letter[1], pos2_letter[1])
                max_col = max(pos1_letter[1], pos2_letter[1])
                # First letter will be at min_col - 1
                # Second letter needs to be at relative position 1 (for space at start)
                # Last letter needs to be at a position that leaves enough space
                skeleton = {}
                if pos1_letter[1] == min_col:
                    skeleton[1] = letter1.upper()  # First letter gets position 1
                    skeleton[max_col - min_col + 1] = letter2.upper()  # Second letter gets correct spacing
                else:
                    skeleton[1] = letter2.upper()  # First letter gets position 1
                    skeleton[max_col - min_col + 1] = letter1.upper()  # Second letter gets correct spacing
                bridge_start_pos = (pos1_letter[0], min_col)  # Start at the first letter's column
                # DEBUG - Show skeleton and letter details
                print("=" * 50)
                print("*** Bridge word search info ***")
                print(f"Word1: {word1} at {pos1}, dir1: {dir1}")
                print(f"Word2: {word2} at {pos2}, dir2: {dir2}")
                print(f"Letter1: {letter1} at {pos1_letter}")
                print(f"Letter2: {letter2} at {pos2_letter}")
                print(f"Bridge direction: {bridge_direction}")
                print(f"Skeleton: {skeleton}")
                print(f"Bridge start pos: {bridge_start_pos}")
                print("Letter availability:")
                print(f"- Available letters: {sorted(available_letters)}")
                print(f"- Letter counts: {available_letter_counts}")
                print("Skeleton details:")
                print(f"- min_col={min_col}, max_col={max_col}, spacing={max_col-min_col+1}")
                print(f"- Looking for word with {letter1} at 1 and {letter2} at {max_col-min_col+1}")

            # Try to find words that fit the skeleton
            found_words = gaddag.find_words_with_skeleton(skeleton, available_letters)
            print(f"Skeleton gives words: {found_words}")
            
            for bridge_word in found_words:
                # Simplified scoring: favor shorter bridges.  Could be refined.
                score = -len(bridge_word)
                candidates.append(ConnectionCandidate(score, word1, word2, bridge_word, bridge_start_pos, bridge_direction))

    return candidates
def phase_de_connexion(
    grille: Board,
    mots_a_reviser: Set[str],
    mots_places: Set[str],
    graphe: ScrabbleGraph,
    orientations: Dict[str, Tuple[Tuple[int, int], Direction]],
    dictionnaire: Set[str],
    lettres_appui: Dict[str, Dict[str, int]],
    distance_max: int,
    lettres_disponibles: Dict[str, int],
    gaddag: GADDAG
) -> bool:
    """Connects isolated words."""
    connections_made = False

    # Initialize graph with ALL words.
    for mot in mots_places.union(mots_a_reviser):
        if mot not in graphe.nodes and mot in orientations:
            position, direction = orientations[mot]
            graphe.add_word(mot, position, direction)

    unconnected_words, distances = graphe.get_unconnected_words()
    sorted_unconnected = sorted(unconnected_words, key=lambda w: distances.get(w, float('inf')))

    for mot1 in sorted_unconnected:
        node1 = graphe.nodes[mot1]
        pos1, dir1 = node1.position, node1.direction

        # Find closest connected word (prioritize central word).
        closest_connected_word = graphe.central_word if graphe.central_word and graphe.central_word != mot1 else None
        min_distance = distances.get(graphe.central_word, float('inf')) if closest_connected_word else float('inf')

        if not closest_connected_word or min_distance == float('inf'):
            for mot2 in graphe.nodes:
                if mot1 != mot2 and graphe.union_find.are_connected(graphe.central_word, mot2):
                    distance = distances.get(mot2, float('inf'))
                    if distance < min_distance:
                        min_distance, closest_connected_word = distance, mot2

        if not closest_connected_word:
            continue

        mot2 = closest_connected_word
        node2 = graphe.nodes[mot2]
        pos2, dir2 = node2.position, node2.direction

        # --- Connection Logic ---
        v_sep, h_sep = calculate_separation(pos1, dir1, len(mot1), pos2, dir2, len(mot2))
        if not is_valid_word_placement(v_sep, h_sep, dir1, dir2, D_MAX):
            continue

        # NO DIRECT INTERSECTION CHECK

        bridge_candidates = find_bridge_words(mot1, pos1, dir1, mot2, pos2, dir2, lettres_appui, gaddag, lettres_disponibles)
        if bridge_candidates:
            best_candidate = sorted(bridge_candidates, key=lambda x: x.score, reverse=True)[0]
            grille.place_word(best_candidate.bridge_word, best_candidate.bridge_pos, best_candidate.bridge_direction)
            graphe.add_word(best_candidate.bridge_word, best_candidate.bridge_pos, best_candidate.bridge_direction)

            # Create connections in the graph (using get_letter_position).
            # Connection 1: mot1 to bridge word
            # Find support letter positions for mot1
            if mot1 in lettres_appui:
                for letter, idx in lettres_appui[mot1].items():
                    pos1_letter = get_letter_position(pos1, idx, dir1)
                    print(f"Checking support letter {letter} at pos {pos1_letter}")
                    for i_bridge, letter_bridge in enumerate(best_candidate.bridge_word):
                        pos_bridge_letter = get_letter_position(best_candidate.bridge_pos, i_bridge, best_candidate.bridge_direction)
                        print(f"  Against bridge letter {letter_bridge} at pos {pos_bridge_letter}")
                        if pos1_letter == pos_bridge_letter:
                            print(f"Found intersection mot1={mot1} support_letter={letter} at pos={pos1_letter}")
                            graphe.add_connection(Connection(mot1, best_candidate.bridge_word, pos1_letter, letter, True))
                            break

            # Connection 2: bridge word to mot2
            # Find support letter positions for mot2
            if mot2 in lettres_appui:
                for letter, idx in lettres_appui[mot2].items():
                    pos2_letter = get_letter_position(pos2, idx, dir2)
                    print(f"Checking support letter {letter} at pos {pos2_letter}")
                    for i_bridge, letter_bridge in enumerate(best_candidate.bridge_word):
                        pos_bridge_letter = get_letter_position(best_candidate.bridge_pos, i_bridge, best_candidate.bridge_direction)
                        print(f"  Against bridge letter {letter_bridge} at pos {pos_bridge_letter}")
                        if pos2_letter == pos_bridge_letter:
                            print(f"Found intersection mot2={mot2} support_letter={letter} at pos={pos2_letter}")
                            graphe.add_connection(Connection(best_candidate.bridge_word, mot2, pos2_letter, letter, True))
                            break
            connections_made = True

    return connections_made