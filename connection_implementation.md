
**Overall Goal:**

The primary goal of the connection algorithm is to take a Scrabble board with potentially isolated words (words not touching any other words) and create valid connections between them.  These connections can be either:


*   **Bridge Words:** If two words are parallel or are perpendicular but *don't* intersect, we need to find one or more "bridge words" to connect them.  These bridge words must form valid Scrabble words with letters from the original words.

**Data Structures:**

*   **`Board`:** Represents the Scrabble board (grid of letters).  Used for placing bridge words and checking for overlaps.
*   **`ScrabbleGraph`:** A graph where:
    *   **Nodes:** Represent words on the board.
    *   **Edges:** Represent connections between words (either direct intersections or via bridge words).
    *   Uses a `UnionFind` data structure to efficiently track connected components (groups of words that are connected to each other).
*   **`GADDAG`:** A specialized data structure for efficiently finding words that match certain patterns (used to find bridge words).
*   **`Connection` (NamedTuple):** Represents a single connection between two words, storing the words, the intersection point, the common letter, and whether it's a support letter.
*   **`ConnectionCandidate` (dataclass):** Represents a potential bridge word, along with its score and other relevant information.
*   **`orientations` (Dictionary):** Stores the position `Tuple[int, int]` and direction (`Direction`) of *every* word on the board (both those to be revised and those already placed). This is *crucial* for initializing the `ScrabbleGraph`.
*    **`lettres_appui`**: Support letters

**Algorithm Steps (within `phase_de_connexion`):**

1.  **Initialization:**

    *   The function receives:
        *   `grille`: The `Board` object.
        *   `mots_a_reviser`:  A set of words that need to be connected.
        *   `mots_places`: A set of *all* words currently on the board (including `mots_a_reviser`).
        *   `graphe`: The `ScrabbleGraph` object.
        *   `orientations`: A dictionary mapping word -> (position, direction).
        *   `dictionnaire`: A set of valid words (not directly used in the current code, but potentially useful for validation).
        *   `lettres_appui`: A dictionary mapping word -> {letter -> position index}.
        *   `distance_max`:  A maximum distance (not currently used, but could be a future constraint).
        *   `lettres_disponibles`:  A dictionary of available letters (for bridge word creation).
        *   `gaddag`: The `GADDAG` object.

    *   **Build the Graph:** The code iterates through *all* words (`mots_places` union `mots_a_reviser`) and adds them to the `ScrabbleGraph`. This creates the initial graph structure, where each word is an isolated node.  The `orientations` dictionary is *essential* here; it provides the position and direction of each word.

2.  **Identify Unconnected Words:**

    *   `graphe.get_unconnected_words()`: This method uses the `UnionFind` data structure within the `ScrabbleGraph` to efficiently determine which words are *not* connected to the `central_word`.  It returns:
        *   `unconnected_words`: A set of unconnected words.
        *   `distances`: A dictionary mapping each unconnected word to its *graph distance* from the central word (or infinity if no path exists). This distance is the number of connections (edges) in the shortest path, *not* the grid distance.

3.  **Prioritize Unconnected Words:**

    *   `sorted_unconnected = sorted(unconnected_words, key=lambda w: distances.get(w, float('inf')))`:  The unconnected words are sorted by their distance from the central word.  Words closer to the central word (or other connected words) are prioritized for connection. This is a heuristic to improve the chances of finding connections quickly.

4.  **Iterate and Connect:**

    *   The code iterates through the `sorted_unconnected` words (attempting to connect them one by one).
    *   For each `mot1` (the unconnected word):
        *   **Find Closest Connected Word:** The algorithm tries to find the closest word (`mot2`) that is *already* connected to the central word (or to a word that's connected to the central word, and so on).  It prioritizes the central word itself, then checks other connected words.
        *   **Geometric Validity Check:**
            *   `calculate_separation(...)`: Calculates the vertical and horizontal separation between `mot1` and `mot2`.
            *   `is_valid_word_placement(...)`: Checks if the two words are too close (for parallel words) or violate board boundaries.  If the placement is invalid, it skips to the next potential connection.

        *   **Attempt Bridge Word Connection:**
            *   If there's no direct intersection, the algorithm tries to find bridge words:
                *   `find_bridge_words(...)`: This function uses the `GADDAG` to find potential bridge words. It considers:
                    *   All possible letter combinations between `mot1` and `mot2`.
                    *   The required direction of the bridge word (perpendicular to both `mot1` and `mot2`).
                    *   The available letters (`lettres_disponibles`).
                    *   It generates "skeletons" for the `gaddag.find_words_with_skeleton` method, representing the positions of the letters from `mot1` and `mot2` within the potential bridge word.
                    * It returns of `ConnectionCandidate`
                *   **Choose Best Candidate:** If bridge words are found, the best candidate (currently, the shortest word) is selected.
                *   **Place Bridge Word and Update Graph:**
                    *   `grille.placer_mot(...)`: The bridge word is placed on the `Board`.
                    *   `graphe.add_word(...)`: The bridge word is added to the `ScrabbleGraph`.
                    *   `find_intersection_point(...)`:  Find the intersection point.
                    *   `graphe.add_connection(...)`: *Two* connections are added to the graph: one between `mot1` and the bridge word, and another between the bridge word and `mot2`.

5.  **Return Value:**

    *   The `phase_de_connexion` function returns `True` if *any* connections were made, and `False` otherwise. This can be used to determine if further connection attempts are needed.

**Key Functions Explained:**

*   **`calculate_separation(pos1, dir1, len1, pos2, dir2, len2)`:** Calculates the vertical and horizontal separation between two words, given their positions, directions, and lengths.  Handles parallel and perpendicular cases.

*   **`is_valid_word_placement(v_sep, h_sep, dir1, dir2, d_max)`:** Checks if the geometric arrangement of two words is valid based on separation and board boundaries.

*   **`get_letter_position(start_pos, index, direction)`:**  Calculates the board coordinates (row, col) of a letter within a word, given the word's starting position, the letter's index within the word, and the word's direction.

*   **`find_intersection_point(word1, pos1, dir1, word2, pos2, dir2, lettres_appui)`:**  Checks if two perpendicular words intersect at a common letter (or use a support letter).

*   **`find_bridge_words(word1, pos1, dir1, word2, pos2, dir2, lettres_appui, gaddag, lettres_disponibles)`:**  The core function for finding bridge words.  It uses the `GADDAG` to find words that can connect two given words, based on their positions, directions, support letters, and available letters.

*   **`ScrabbleGraph` Methods:**
    *   `add_word(mot, position, direction)`: Adds a word to the graph.
    *   `add_connection(connection)`: Adds a connection between two words in the graph.
    *   `get_unconnected_words()`: Returns a set of words not connected to the central word and their distances.
    *   `get_shortest_path(mot1, mot2)`: (Not directly used in the final version, but part of the graph structure). Finds the shortest path between two words in the graph.

**In Summary:**

The algorithm efficiently connects isolated words on a Scrabble board by:

1.  Representing the board state as a graph.
2.  Using a Union-Find data structure to track connected components.
3.  Prioritizing connections based on distance to the central word.
4.  Attempting direct intersections first.
5.  Using a GADDAG to find bridge words when direct intersections are not possible.
6.  Enforcing geometric constraints.
7.  Updating the graph and board state after each successful connection.

This detailed explanation, combined with the well-commented code, should provide a complete understanding of the connection algorithm. This breakdown clarifies how all the pieces work together to achieve the goal of connecting isolated words on the Scrabble board.
