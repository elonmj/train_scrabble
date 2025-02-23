import pytest
from typing import Dict, Set, Tuple
from src.models.types import Direction
from src.models.board import Board
from src.models.gaddag import GADDAG
from src.models.graph import ScrabbleGraph, Connection, UnionFind, WordNode
from src.modules.connection import (
    calculate_separation,
    is_valid_word_placement,
    get_letter_position,
    find_bridge_words,
    phase_de_connexion,
    ConnectionCandidate
)
from unittest.mock import MagicMock, call

# --- Fixtures ---

@pytest.fixture
def gaddag():
    g = GADDAG()
    g.add_word("MILITA")  # Bridge word using MI from MAISON and IT from VIOLEE
    g.add_word("MAISON")
    g.add_word("PAPIER")
    g.add_word("VIOLEE")
    g.add_word("DIRAIT")  # Bridge word using IR from PAPIER and AIT from PATIER
    g.add_word("PATIER")
    g.add_word("OSAIT")   # Bridge word using OS from MAISON and AIT from PAPIER
    return g

@pytest.fixture(scope="session") # Load once per session
def gaddag_loaded():
    import os
    g = GADDAG()
    dict_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_dicts.txt")
    words_loaded = g.load_dictionary(dict_path)
    print(f"Loaded {words_loaded} words from test_dicts.txt")
    # Verify OSAIT is loaded
    assert g.contains("OSAIT"), "OSAIT should be in the GADDAG"
    # Verify OSAIT can be found with skeleton
    skeleton = {1: 'S', 3: 'I'}  # OSAIT: O(0) S(1) A(2) I(3) T(4)
    available = {'O', 'S', 'A', 'I', 'T'}
    words = g.find_words_with_skeleton(skeleton, available)
    print(f"Found words with S-I skeleton: {words}")
    assert "OSAIT" in words, "OSAIT should be found with S-I skeleton"
    return g

@pytest.fixture
def empty_graph():
    return ScrabbleGraph()

@pytest.fixture
def board():
    return Board()

@pytest.fixture
def sample_graph(gaddag):
    graph = ScrabbleGraph()
    graph.add_word("MAISON", (4, 5), Direction.HORIZONTAL)
    graph.add_word("PAPIER", (4, 7), Direction.VERTICAL) # Intersects with MAISON
    graph.central_word = "MAISON"
    graph.add_connection(Connection("MAISON", "PAPIER", (4, 7), "P", False)) # Direct connection

    return graph

# --- UnionFind Tests --- (No changes needed here)

def test_union_find_initialization():
    uf = UnionFind()
    assert uf.parent == {}
    assert uf.rank == {}
    assert uf.size == {}

def test_union_find_make_set():
    uf = UnionFind()
    uf.make_set("WORD")
    assert uf.parent["WORD"] == "WORD"
    assert uf.rank["WORD"] == 0
    assert uf.size["WORD"] == 1

def test_union_find_find():
    uf = UnionFind()
    uf.make_set("WORD1")
    uf.make_set("WORD2")
    assert uf.find("WORD1") == "WORD1"
    assert uf.find("WORD2") == "WORD2"
    uf.union("WORD1", "WORD2")
    assert uf.find("WORD1") == uf.find("WORD2")

def test_union_find_union():
    uf = UnionFind()
    uf.make_set("A")
    uf.make_set("B")
    uf.make_set("C")
    uf.union("A", "B")
    assert uf.are_connected("A", "B")
    assert not uf.are_connected("A", "C")
    uf.union("B", "C")
    assert uf.are_connected("A", "C")
    assert uf.get_component_size("A") == 3

def test_union_find_edge_cases():
    uf = UnionFind()
    # Test finding a word that hasn't been added yet
    assert uf.find("NEWWORD") == "NEWWORD"
    #Test union with self
    uf.union("NEWWORD", "NEWWORD")
    assert uf.are_connected("NEWWORD", "NEWWORD")

# --- ScrabbleGraph Tests --- (No changes needed here)

def test_scrabble_graph_add_word(empty_graph):
    empty_graph.add_word("TEST", (1, 1), Direction.HORIZONTAL)
    assert "TEST" in empty_graph.nodes
    assert empty_graph.nodes["TEST"].position == (1, 1)
    assert empty_graph.nodes["TEST"].direction == Direction.HORIZONTAL
    assert "TEST" in empty_graph.union_find.parent
    assert "TEST" in empty_graph.expected_words

def test_scrabble_graph_add_connection(sample_graph):
    # Add word and connection
    sample_graph.add_word("VIOLEE", (6, 5), Direction.HORIZONTAL)
    sample_graph.add_connection(Connection("PAPIER", "VIOLEE", (6, 7), "E", False, 1))
    assert len(sample_graph.nodes["PAPIER"].connections) == 2
    assert len(sample_graph.nodes["VIOLEE"].connections) == 1
    assert sample_graph.union_find.are_connected("MAISON", "VIOLEE")

def test_scrabble_graph_get_shortest_path(sample_graph):
    # Test existing connection
    path = sample_graph.get_shortest_path("MAISON", "PAPIER")
    assert path == [Connection("MAISON", "PAPIER", (4, 7), "P", False)]

    # Test no path
    sample_graph.add_word("ISOLATED", (10, 10), Direction.HORIZONTAL)
    path = sample_graph.get_shortest_path("MAISON", "ISOLATED")
    assert path is None

    #Test path after adding connection.
    sample_graph.add_connection(Connection("PAPIER", "ISOLATED", (7,10), "I", False)) #Connect them
    path = sample_graph.get_shortest_path("MAISON", "ISOLATED")
    assert len(path) == 2
    assert path[0] == Connection("MAISON", "PAPIER", (4, 7), "P", False)
    assert path[1] == Connection("PAPIER", "ISOLATED", (7,10), "I", False)

def test_scrabble_graph_get_all_paths(sample_graph):
     # Add a cycle
    sample_graph.add_word("WORD3", (2,7), Direction.VERTICAL)
    sample_graph.add_connection(Connection("MAISON", "WORD3", (2, 7), "M", False))
    sample_graph.add_connection(Connection("WORD3", "PAPIER", (4, 7), "P", False))


    paths = sample_graph.get_all_paths("MAISON", "PAPIER")
    assert len(paths) == 2  # Expect two paths: direct and via WORD3

    #Test with max_length
    paths = sample_graph.get_all_paths("MAISON", "PAPIER", max_length=1)
    assert len(paths) == 1  #Only the direct path

    #Test no paths
    sample_graph.add_word("ISOLATED", (10, 10), Direction.HORIZONTAL)
    paths = sample_graph.get_all_paths("MAISON", "ISOLATED")
    assert paths == []

def test_scrabble_graph_get_unconnected_words(sample_graph):
    sample_graph.add_word("ISOLATED", (10, 10), Direction.HORIZONTAL)
    unconnected, distances = sample_graph.get_unconnected_words()
    assert "ISOLATED" in unconnected
    assert distances["ISOLATED"] == float('inf')
    assert "PAPIER" not in unconnected  # PAPIER is connected

    # Test with no central word
    sample_graph.central_word = None
    unconnected, distances = sample_graph.get_unconnected_words()
    assert len(unconnected) == 3 #All words are unconnected when there is no central word
    assert distances["ISOLATED"] == float('inf')
    assert distances["PAPIER"] == float('inf')


def test_scrabble_graph_update_distances(sample_graph):
    # Test initial distances
    assert sample_graph.distances["MAISON"]["MAISON"] == 0
    assert sample_graph.distances["MAISON"]["PAPIER"] == 1
    assert sample_graph.distances["PAPIER"]["MAISON"] == 1
    # Add a new word and connection
    sample_graph.add_word("NEWWORD", (10, 5), Direction.HORIZONTAL)
    sample_graph.add_connection(Connection("MAISON", "NEWWORD", (5,5), "N", False))
     # Check that the new word distances are set:
    assert sample_graph.distances["MAISON"]["NEWWORD"] == 1
    assert sample_graph.distances["NEWWORD"]["MAISON"] == 1
    assert sample_graph.distances["NEWWORD"]["PAPIER"] == 2
    assert sample_graph.distances["PAPIER"]["NEWWORD"] == 2

def test_scrabble_graph_validate_path(sample_graph):

    #Valid path
    path1 = [Connection("MAISON", "PAPIER", (4, 7), "P", False)]
    assert sample_graph.validate_path(path1) == False # no support letter

    path2 = [Connection("MAISON", "PAPIER", (4, 7), "P", True)]
    assert sample_graph.validate_path(path2) == True # support letter

    #Invalid path
    sample_graph.add_word("WORD3", (2,7), Direction.VERTICAL)
    path3 = [Connection("MAISON", "PAPIER", (4,7), "P", False), Connection("WORD3", "MAISON", (2,5), "M", False)] #Disconnected path
    assert sample_graph.validate_path(path3) == False
    #Empty path
    assert sample_graph.validate_path([]) == False

# --- calculate_separation Tests --- (No changes needed here)

@pytest.mark.parametrize(
    "pos1, dir1, len1, pos2, dir2, len2, expected",
    [
        ((4, 5), Direction.HORIZONTAL, 6, (8, 5), Direction.HORIZONTAL, 6, (4, 0)),  # No overlap
        ((4, 5), Direction.HORIZONTAL, 6, (8, 7), Direction.HORIZONTAL, 6, (4, 0)),  # Partial overlap should be 0
        ((4, 5), Direction.VERTICAL, 6, (4, 8), Direction.VERTICAL, 6, (0, 3)),      # No overlap
        ((4, 5), Direction.VERTICAL, 6, (5, 8), Direction.VERTICAL, 6, (0, 3)),      # Partial overlap should be 0
        ((4, 5), Direction.HORIZONTAL, 6, (4, 8), Direction.VERTICAL, 6, (0, 3)),   # Perpendicular
        ((4, 5), Direction.HORIZONTAL, 3, (4, 8), Direction.HORIZONTAL, 3, (0, 0)),  # No overlap should be 0
        ((4, 5), Direction.HORIZONTAL, 3, (4, 6), Direction.HORIZONTAL, 3, (0, 0)),   # Partial
    ]
)
def test_calculate_separation(pos1, dir1, len1, pos2, dir2, len2, expected):
    assert calculate_separation(pos1, dir1, len1, pos2, dir2, len2) == expected

# --- is_valid_word_placement Tests --- (No changes needed here)

@pytest.mark.parametrize(
    "v_sep, h_sep, dir1, dir2, d_max, expected",
    [
        (2, 0, Direction.HORIZONTAL, Direction.HORIZONTAL, 15, True),  # Valid horizontal
        (1, 0, Direction.HORIZONTAL, Direction.HORIZONTAL, 15, False), # Invalid horizontal (too close)
        (0, 2, Direction.VERTICAL, Direction.VERTICAL, 15, True),      # Valid vertical
        (0, 1, Direction.VERTICAL, Direction.VERTICAL, 15, False),     # Invalid vertical (too close)
        (5, 5, Direction.HORIZONTAL, Direction.VERTICAL, 15, True),    # Perpendicular - always valid
    ]
)
def test_is_valid_word_placement(v_sep, h_sep, dir1, dir2, d_max, expected):
    assert is_valid_word_placement(v_sep, h_sep, dir1, dir2, d_max) == expected

# --- get_letter_position Tests --- (No changes needed here)

@pytest.mark.parametrize(
    "pos, index, direction, expected",
    [
        ((5, 5), 0, Direction.HORIZONTAL, (5, 5)),
        ((5, 5), 2, Direction.HORIZONTAL, (5, 7)),
        ((5, 5), 0, Direction.VERTICAL, (5, 5)),
        ((5, 5), 2, Direction.VERTICAL, (7, 5)),
        ((0, 0), 4, Direction.HORIZONTAL, (0, 4)), #Edge case
        ((0, 0), 4, Direction.VERTICAL, (4, 0)) #Edge case
    ]
)
def test_get_letter_position(pos, index, direction, expected):
    assert get_letter_position(pos, index, direction) == expected

# --- find_bridge_words Tests ---

def test_find_bridge_words_no_bridge(gaddag_loaded):
    # Words that cannot be bridged (too far, no possible words)
    lettres_appui = {}
    lettres_disponibles = {"X": 1, "Y": 1, "Z": 1}
    result = find_bridge_words(
        "MAISON", (1, 1), Direction.HORIZONTAL,
        "PAPIER", (1, 14), Direction.HORIZONTAL,  # Too far apart
        lettres_appui, gaddag_loaded, lettres_disponibles
    )
    assert result == []

def test_find_bridge_words_horizontal_bridge(gaddag_loaded):
    # Test finding bridge word between two horizontal words
    # Example from documentation: MAISON and PAPIER connected by OSAIT
    # S and I must be in column H (col 7)
    lettres_appui = {
        "MAISON": {"S": 2},  # S is third letter (position 2) in MAISON
        "PAPIER": {"I": 2}   # I is third letter (position 2) in PAPIER
    }
    # Only the letters needed to form OSAIT
    lettres_disponibles = {"O": 1, "S": 1, "A": 1, "I": 1, "T": 1}
    # Following the example grid from documentation
    candidates = find_bridge_words(
        "MAISON", (4, 5), Direction.HORIZONTAL,  # MAISON starts at row 4, col 5
        "PAPIER", (6, 5), Direction.HORIZONTAL,  # PAPIER starts at row 6, col 5
        lettres_appui, gaddag_loaded, lettres_disponibles
    )
    assert len(candidates) > 0

    # Check that OSAIT is found as a vertical bridge word
    # It should connect S from MAISON and I from PAPIER in column H (index 7)
    found_osait = False
    for candidate in candidates:
        if candidate.bridge_word == "OSAIT":
            found_osait = True
            assert candidate.bridge_direction == Direction.VERTICAL
            assert candidate.bridge_pos == (3, 7)  # OSAIT starts at row 3, col 7 (column H)
            assert candidate.score == -5  # Length of OSAIT
            break
    assert found_osait, "Should find OSAIT as bridge word using S from MAISON and I from PAPIER in column H"

def test_find_bridge_words_vertical_bridge(gaddag_loaded):
    # Test finding bridge words between two vertical words
    # Example from documentation: MAISON and PATIER connected by DIRAIT in row 5
    lettres_appui = {
        "MAISON": {"I": 2},  # I is third letter (index 2) in MAISON
        "PATIER": {"T": 2}   # T is third letter (index 2) in PATIER
    }
    lettres_disponibles = {"D": 1, "I": 1, "R": 1, "A": 1, "T": 1}  # Letters needed for DIRAIT

    candidates = find_bridge_words(
        "MAISON", (3, 4), Direction.VERTICAL,   # MAISON starts at (3,4)
        "PATIER", (3, 8), Direction.VERTICAL,   # PATIER starts at (3,8)
        lettres_appui, gaddag_loaded, lettres_disponibles
    )
    assert len(candidates) > 0

    # Check for DIRAIT as bridge word
    found_dirait = False
    for candidate in candidates:
        if candidate.bridge_word == "DIRAIT":
            found_dirait = True
            assert candidate.bridge_direction == Direction.HORIZONTAL
            assert candidate.bridge_pos == (5, 4)  # DIRAIT starts at row 5, col 4
            assert candidate.score == -6
            break
    assert found_dirait, "Should find DIRAIT as bridge word using I from MAISON and T from PATIER in row 5"

# --- phase_de_connexion Tests ---

def test_phase_de_connexion_no_connections(gaddag_loaded):
    # No possible connections (words too far apart)
    board_mock = MagicMock(spec=Board)
    board_mock.placer_mot = MagicMock()  # Add the method to the mock
    graph = ScrabbleGraph()
    graph.add_word("MAISON", (4, 5), Direction.HORIZONTAL)
    graph.add_word("PAPIER", (10, 10), Direction.HORIZONTAL)  # Too far
    graph.central_word = 'MAISON'
    mots_a_reviser = {"PAPIER"}
    mots_places = {"MAISON"}
    orientations = {
        "MAISON": ((4, 5), Direction.HORIZONTAL),
        "PAPIER": ((10, 10), Direction.HORIZONTAL)
    }
    lettres_appui = {}
    lettres_disponibles = {"X": 1, "Y": 1, "Z": 1}

    result = phase_de_connexion(
        board_mock, mots_a_reviser, mots_places, graph, orientations,
        set(), lettres_appui, 15, lettres_disponibles, gaddag_loaded
    )
    assert result is False
    board_mock.placer_mot.assert_not_called() # Shouldn't be called

def test_phase_de_connexion_successful_connection(gaddag_loaded, board):
    board_mock = MagicMock(spec=Board)
    board_mock.placer_mot = MagicMock()  # Add the method to the mock
    graph = ScrabbleGraph()
    graph.add_word("MAISON", (4, 5), Direction.HORIZONTAL)
    graph.add_word("PAPIER", (6, 5), Direction.HORIZONTAL)
    graph.central_word = "MAISON"

    mots_a_reviser = {"PAPIER"}
    mots_places = {"MAISON"}
    orientations = {
        "MAISON": ((4, 5), Direction.HORIZONTAL),
        "PAPIER": ((6, 5), Direction.HORIZONTAL)
    }
    # Use the same example as the documentation with OSAIT bridge word
    # S and I must be in column H (col 7)
    lettres_appui = {
        "MAISON": {"S": 2},  # S is third letter (position 2) in MAISON
        "PAPIER": {"I": 2}   # I is third letter (position 2) in PAPIER
    }
    lettres_disponibles = {"O": 1, "S": 1, "A": 1, "I": 1, "T": 1}  # Letters needed for OSAIT

    result = phase_de_connexion(
        board_mock, mots_a_reviser, mots_places, graph, orientations,
        set(), lettres_appui, 15, lettres_disponibles, gaddag_loaded
    )

    assert result is True
    assert "OSAIT" in graph.nodes
    assert graph.union_find.are_connected("MAISON", "PAPIER")

    # Check that OSAIT was placed correctly
    expected_calls = [
        call("OSAIT", (3, 7), Direction.VERTICAL, is_place_definitive=True)
    ]
    board_mock.placer_mot.assert_has_calls(expected_calls)

    # Check that OSAIT connects using the correct letters
    connections = graph.nodes["MAISON"].connections
    assert len(connections) == 1
    assert connections[0].lettre == "S", "Connection should use S from MAISON"
    assert connections[0].position == (4, 7), "Connection should be at column H (index 7)"
    assert connections[0].est_appui is True, "S should be marked as a support letter"

    connections = graph.nodes["PAPIER"].connections
    assert len(connections) == 1
    assert connections[0].lettre == "I", "Connection should use I from PAPIER"
    assert connections[0].position == (6, 7), "Connection should be at column H (index 7)"
    assert connections[0].est_appui is True, "I should be marked as a support letter"

    # Verify OSAIT has two connections (one to each word)
    connections = graph.nodes["OSAIT"].connections
    assert len(connections) == 2, "OSAIT should connect to both MAISON and PAPIER"

def test_phase_de_connexion_no_central_word(gaddag_loaded):
    board_mock = MagicMock(spec=Board)
    board_mock.placer_mot = MagicMock()  # Add the method to the mock
    graph = ScrabbleGraph()
    graph.add_word('WORD1', (1,1), Direction.HORIZONTAL)
    graph.add_word('WORD2', (3,3), Direction.HORIZONTAL)

    mots_a_reviser = {'WORD1', 'WORD2'}
    mots_places = set()
    orientations = {
        'WORD1': ((1,1), Direction.HORIZONTAL),
        'WORD2': ((3,3), Direction.HORIZONTAL)
    }
    lettres_appui = {}
    lettres_disponibles = {}

    result = phase_de_connexion(board_mock, mots_a_reviser, mots_places, graph, orientations, set(), lettres_appui, 15, lettres_disponibles, gaddag_loaded)
    assert result == False
    board_mock.placer_mot.assert_not_called()


def test_phase_de_connexion_already_connected(gaddag_loaded, sample_graph):
    board_mock = MagicMock(spec=Board)
    board_mock.placer_mot = MagicMock()  # Add the method to the mock

    mots_a_reviser = {"PAPIER"}
    mots_places = {'MAISON'}
    orientations = {
        'MAISON': ((4,5), Direction.HORIZONTAL),
        'PAPIER': ((4,7), Direction.VERTICAL)
    }
    lettres_appui = {}
    lettres_disponibles = {}
    result = phase_de_connexion(
        board_mock, mots_a_reviser, mots_places, sample_graph, orientations,
        set(), lettres_appui, 15, lettres_disponibles, gaddag_loaded
        )
    assert result == False #No NEW connections made
    board_mock.placer_mot.assert_not_called()