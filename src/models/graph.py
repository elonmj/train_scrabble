from typing import Dict, Set, Optional, List, Tuple, NamedTuple
from collections import defaultdict, deque
from ..models.types import Direction  # Corrected relative import
from ..models.board import Board

class Connection(NamedTuple):
    """Représente une connexion entre deux mots."""
    mot1: str
    mot2: str
    position: Tuple[int, int]  # Position de l'intersection
    lettre: str  # Lettre commune
    est_appui: bool  # True si c'est une lettre d'appui
    distance: int = 1  # Distance between words in the graph (always 1 in our case)

class UnionFind:
    """Efficient data structure for tracking connected components."""
    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}
        self.size: Dict[str, int] = {}  # Track size of each component

    def make_set(self, word: str) -> None:
        """Initialize a new set with a single word."""
        self.parent[word] = word
        self.rank[word] = 0
        self.size[word] = 1

    def find(self, word: str) -> str:
        """Find the representative of word's set with path compression."""
        if word not in self.parent:
            self.make_set(word)
            return word
        if self.parent[word] != word:
            self.parent[word] = self.find(self.parent[word])
        return self.parent[word]

    def union(self, word1: str, word2: str) -> None:
        """Unite two sets using union by rank."""
        root1 = self.find(word1)
        root2 = self.find(word2)
        if root1 != root2:
            if self.rank[root1] < self.rank[root2]:
                root1, root2 = root2, root1
            self.parent[root2] = root1
            self.size[root1] += self.size[root2]
            if self.rank[root1] == self.rank[root2]:
                self.rank[root1] += 1

    def get_component_size(self, word: str) -> int:
        """Get the size of the component containing word."""
        return self.size[self.find(word)]

    def are_connected(self, word1: str, word2: str) -> bool:
        """Check if two words are in the same component."""
        return self.find(word1) == self.find(word2)

class WordNode:
    """Représente un nœud (mot) dans le graphe."""
    def __init__(self, mot: str, position: Tuple[int, int], direction: Direction):
        self.mot = mot
        self.position = position  # Position de début du mot
        self.direction = direction
        self.connections: List[Connection] = []  # Liste des connexions
        self.degree: int = 0  # Number of connections

class ScrabbleGraph:
    """Graphe optimisé pour représenter une grille de Scrabble."""
    def __init__(self, board: Optional[Board] = None):
        self.board = board
        self.nodes: Dict[str, WordNode] = {}  # mot -> nœud
        self.central_word: Optional[str] = None  # Mot central
        self.lettres_appui: Dict[str, Dict[str, int]] = {}  # mot -> {lettre -> position}
        self.expected_words: Set[str] = set()
        self.union_find = UnionFind()
        self.distances: Dict[str, Dict[str, int]] = defaultdict(dict)  # Distances between words
        self.paths: Dict[str, Dict[str, List[Connection]]] = defaultdict(dict)  # Cached paths

    def add_word(self, mot: str, position: Tuple[int, int], direction: Direction) -> None:
        """Ajoute un mot au graphe."""
        if mot not in self.nodes: #Avoid duplicates.
            self.nodes[mot] = WordNode(mot, position, direction)
            self.union_find.make_set(mot)
            self.expected_words.add(mot)
            # Initialize distances and paths for this word.
            self.distances[mot] = {}
            self.paths[mot] = {}


    def get_shortest_path(self, mot1: str, mot2: str) -> Optional[List[Connection]]:
        """Returns the shortest path between two words (BFS)."""
        if mot1 not in self.nodes or mot2 not in self.nodes:
            return None

        if mot2 in self.paths.get(mot1, {}):
            return self.paths[mot1][mot2]

        visited = {mot1}
        queue = deque([(mot1, [])])

        while queue:
            current, current_path = queue.popleft()
            if current == mot2:
                self.paths[mot1][mot2] = current_path  # Cache the path
                return current_path

            node = self.nodes[current]
            for conn in node.connections:
                next_word = conn.mot2
                if next_word not in visited:
                    visited.add(next_word)
                    new_path = current_path + [conn]
                    queue.append((next_word, new_path))

        return None

    def get_all_paths(self, mot1: str, mot2: str, max_length: Optional[int] = None) -> List[List[Connection]]:
        """Returns all paths between two words (DFS), with optional length limit."""
        if mot1 not in self.nodes or mot2 not in self.nodes:
            return []

        all_paths: List[List[Connection]] = []
        visited = {mot1}

        def dfs(current: str, path: List[Connection]) -> None:
            if current == mot2:
                all_paths.append(path[:])  # Append a copy of the path
                return
            if max_length is not None and len(path) >= max_length:
                return

            node = self.nodes[current]
            for conn in node.connections:
                next_word = conn.mot2
                if next_word not in visited:
                    visited.add(next_word)
                    path.append(conn)
                    dfs(next_word, path)
                    path.pop()  # Backtrack
                    visited.remove(next_word)  # Backtrack

        dfs(mot1, [])
        return all_paths

    def add_connection(self, connection: Connection) -> None:
        """Adds a connection between two words and updates the graph."""
        if connection.mot1 in self.nodes and connection.mot2 in self.nodes:
            # Add forward connection
            self.nodes[connection.mot1].connections.append(connection)
            self.nodes[connection.mot1].degree += 1

            # Add reverse connection (undirected graph)
            reverse_conn = Connection(
                mot1=connection.mot2,
                mot2=connection.mot1,
                position=connection.position,
                lettre=connection.lettre,
                est_appui=connection.est_appui,
                distance=connection.distance  # Should always be 1
            )
            self.nodes[connection.mot2].connections.append(reverse_conn)
            self.nodes[connection.mot2].degree += 1

            # Update Union-Find and distances
            self.union_find.union(connection.mot1, connection.mot2)
            self._update_distances(connection)
            self._update_distances(reverse_conn)

            # Clear cache only for affected words
            affected_words = {connection.mot1, connection.mot2}
            for word in affected_words:
                self.paths[word].clear()
                # Initialize distance to self if not exists
                if word not in self.distances[word]:
                    self.distances[word][word] = 0

    def get_unconnected_words(self) -> Tuple[Set[str], Dict[str, float]]:
        """Returns unconnected words and their distances to the central word."""
        unconnected = set()
        distances = {}

        if not self.central_word:
            # When no central word, all words have infinite distance
            distances = {word: float('inf') for word in self.expected_words}
            return set(word for word in self.expected_words if word in self.nodes), distances

        for word in self.expected_words:
            if word != self.central_word:
                if word not in self.nodes:
                    unconnected.add(word)
                    distances[word] = float('inf')
                elif not self.union_find.are_connected(self.central_word, word):
                    unconnected.add(word)
                    # Get shortest distance from central word, if exists.
                    shortest_path = self.get_shortest_path(self.central_word, word)
                    distances[word] = len(shortest_path) if shortest_path else float('inf')

        return unconnected, distances

    def _update_distances(self, connection: Connection) -> None:
        """Updates distances in the graph after adding a connection."""
        # First, collect all reachable words using BFS
        reachable_words = set()
        queue = deque([connection.mot1, connection.mot2])
        visited = {connection.mot1, connection.mot2}

        while queue:
            word = queue.popleft()
            reachable_words.add(word)
            for conn in self.nodes[word].connections:
                next_word = conn.mot2
                if next_word not in visited:
                    visited.add(next_word)
                    queue.append(next_word)

        # Initialize distances for all reachable words
        for word1 in reachable_words:
            if word1 not in self.distances:
                self.distances[word1] = {}
            self.distances[word1][word1] = 0  # Distance to self is 0

            for word2 in reachable_words:
                if word2 not in self.distances:
                    self.distances[word2] = {}
                if word1 != word2:
                    if word2 not in self.distances[word1]:
                        self.distances[word1][word2] = float('inf')
                    if word1 not in self.distances[word2]:
                        self.distances[word2][word1] = float('inf')

        # Set direct connection distance
        self.distances[connection.mot1][connection.mot2] = 1
        self.distances[connection.mot2][connection.mot1] = 1

        # Update all distances using Floyd-Warshall algorithm
        for k in reachable_words:
            for i in reachable_words:
                for j in reachable_words:
                    if (self.distances[i].get(k, float('inf')) +
                        self.distances[k].get(j, float('inf'))) < self.distances[i].get(j, float('inf')):
                        dist = self.distances[i][k] + self.distances[k][j]
                        self.distances[i][j] = dist
                        self.distances[j][i] = dist  # Maintain symmetry

    def validate_path(self, path: List[Connection]) -> bool:
        """Validates a path in the graph."""
        if not path:
            return False
        for i in range(len(path) - 1):
            if path[i].mot2 != path[i+1].mot1:
                return False  # Disconnected path
        return any(conn.est_appui for conn in path) #Check if lettres d'appui in path

    def debug_print(self) -> None:
        """Prints the graph's state for debugging."""
        print("--- Scrabble Graph ---")
        print(f"  Central Word: {self.central_word}")
        print(f"  Expected Words: {self.expected_words}")
        print("  Nodes:")
        for word, node in self.nodes.items():
            print(f"    - {word}:")
            print(f"      Position: {node.position}, Direction: {node.direction}")
            print(f"      Degree: {node.degree}")
            print(f"      Connections:")
            for conn in node.connections:
                print(f"        -> {conn.mot2} (at {conn.position}, letter {conn.lettre}, support: {conn.est_appui})")

        print("  Connected Components (Union-Find):")
        components = defaultdict(list)
        for word in self.expected_words:
            components[self.union_find.find(word)].append(word)
        for root, members in components.items():
            print(f"    Component {root}: {members}")

        print("  Distances (from central word, if applicable):")
        if self.central_word and self.central_word in self.distances:
            for word, dist in self.distances[self.central_word].items():
                print(f"    - {self.central_word} -> {word}: {dist}")
        print("-----------------------")

    def update_from_board(self, board: Board, mots_places: Set[str], lettres_appui: Dict[str, Dict[str, int]]) -> None:
        """Updates the graph based on the words placed on the board."""
        for placed_word in mots_places:
            if placed_word not in self.nodes:
                # Word node should already exist, but just in case
                node = WordNode(placed_word, (0, 0), Direction.HORIZONTAL) # Dummy position and direction
                self.nodes[placed_word] = node
                self.union_find.make_set(placed_word)
                self.expected_words.add(placed_word)

        # Iterate through all pairs of placed words to find connections
        placed_words_list = list(mots_places) # Convert set to list for indexing
        for i in range(len(placed_words_list)):
            for j in range(i + 1, len(placed_words_list)):
                mot1 = placed_words_list[i]
                mot2 = placed_words_list[j]
                self._find_and_add_connections(board, mot1, mot2, lettres_appui)

    def _find_and_add_connections(self, board: Board, mot1: str, mot2: str, lettres_appui: Dict[str, Dict[str, int]]) -> None:
        """Finds and adds connections between two words on the board."""
        if mot1 not in self.nodes or mot2 not in self.nodes:
            return

        node1 = self.nodes[mot1]
        node2 = self.nodes[mot2]

        # Check for connections in both directions (horizontal and vertical)
        for dir1, dir2 in [(Direction.HORIZONTAL, Direction.VERTICAL), (Direction.VERTICAL, Direction.HORIZONTAL)]:
            if node1.direction == dir1 and node2.direction == dir2:
                self._check_connection(board, node1, node2, lettres_appui)
            if node1.direction == dir2 and node2.direction == dir1:
                self._check_connection(board, node2, node1, lettres_appui) # Check reversed


    def _check_connection(self, board: Board, node1: WordNode, node2: WordNode, lettres_appui: Dict[str, Dict[str, int]]) -> None:
        """Checks for a connection between two word nodes and adds it if found."""
        word1 = node1.mot
        word2 = node2.mot
        pos1 = node1.position
        pos2 = node2.position
        dir1 = node1.direction
        dir2 = node2.direction

        len1 = len(word1)
        len2 = len(word2)

        # Iterate through letters of word1
        for idx1, letter1 in enumerate(word1):
            # Calculate coordinates for letter1
            x1 = pos1[0] + (idx1 if dir1 == Direction.VERTICAL else 0)
            y1 = pos1[1] + (idx1 if dir1 == Direction.HORIZONTAL else 0)

            # Iterate through letters of word2
            for idx2, letter2 in enumerate(word2):
                # Calculate coordinates for letter2
                x2 = pos2[0] + (idx2 if dir2 == Direction.VERTICAL else 0)
                y2 = pos2[1] + (idx2 if dir2 == Direction.HORIZONTAL else 0)

                # Check if positions overlap
                if (x1, y1) == (x2, y2) and letter1 == letter2:
                    # Found a connection
                    connection = Connection(
                        mot1=word1,
                        mot2=word2,
                        position=(x1, y1),
                        lettre=letter1,
                        est_appui=letter2 in lettres_appui.get(word1, {}) and lettres_appui[word1].get(letter2, -1) == idx1 or
                                  letter1 in lettres_appui.get(word2, {}) and lettres_appui[word2].get(letter1, -1) == idx2
                    )
                    self.add_connection(connection)
                    return # Stop after finding first connection