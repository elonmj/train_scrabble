"""Test suite for GADDAG implementation."""

import os
import time
import pytest
from src.models.gaddag import GADDAG
from typing import Set

@pytest.fixture
def test_dict_path():
    """Path to test dictionary file."""
    return os.path.join(os.path.dirname(__file__), "..", "data", "test_words.txt")

@pytest.fixture
def gaddag(test_dict_path):
    """Initialize and return a GADDAG with test words."""
    gaddag = GADDAG()
    gaddag.load_dictionary(test_dict_path)
    gaddag.semi_minimize()  # Optimize the structure
    return gaddag

def test_load_dictionary(test_dict_path):
    """Test loading dictionary and structure optimization."""
    print("\n=== Test de chargement du dictionnaire ===")
    gaddag = GADDAG()

    # Measure load time
    start_time = time.time()
    words_loaded = gaddag.load_dictionary(test_dict_path)
    load_time = time.time() - start_time

    print(f"Temps de chargement : {load_time:.2f} secondes")
    print(f"Mots chargés : {words_loaded}")

    # Test minimization
    print("\n=== Test de la semi-minimisation ===")
    start_time = time.time()
    gaddag.semi_minimize()
    minimize_time = time.time() - start_time

    stats = gaddag.get_statistics()
    print(f"Temps de minimisation : {minimize_time:.2f} secondes")
    print(f"Nombre de nœuds : {stats['node_count']}")
    print(f"Nombre de transitions : {stats['transition_count']}")

    assert words_loaded > 0
    assert stats['node_count'] > 0
    assert stats['transition_count'] > 0

def test_recherche_mots(gaddag):
    """Test word search in GADDAG."""
    print("\n=== Test de recherche de mots ===")

    test_cases = [
        ("MAISON", True),
        ("JARDIN", True),
        ("CHAT", True),
        ("CHIEN", True),
        ("A", False),      # Too short
        ("LE", True),      # Valid short word
        ("ANTICONSTITUTIONNELLEMENT", False),  # Too long
        ("INVALID", False),  # Not in dictionary
        ("château", True),  # Accented, should find CHATEAU
    ]

    for word, expected in test_cases:
        exists = gaddag.contains(word)
        print(f"Mot '{word}' : {'trouvé' if exists else 'non trouvé'} (attendu: {'oui' if expected else 'non'})")
        assert exists == expected, f"Unexpected result for '{word}'"

        if exists:
            # Test prefixes
            for i in range(2, len(word)):
                prefix = word[:i]
                suffixes = gaddag.get_possible_letters(prefix.upper())
                if suffixes:
                    print(f"- Après '{prefix}': {sorted(suffixes)}")
                    assert len(suffixes) > 0

def test_ajout_mot(gaddag):
    """Test adding new words."""
    print("\n=== Test d'ajout de mots ===")

    test_words = ["TABLE", "JARDIN", "FLEUR"]

    for word in test_words:
        print(f"\nAjout du mot '{word}':")
        stats_before = gaddag.get_statistics()

        gaddag.add_word(word.upper())

        stats_after = gaddag.get_statistics()
        nodes_added = stats_after['node_count'] - stats_before['node_count']
        transitions_added = stats_after['transition_count'] - stats_before['transition_count']

        print(f"- Nœuds ajoutés : {nodes_added}")
        print(f"- Transitions ajoutées : {transitions_added}")
        print(f"- Le mot existe maintenant : {gaddag.contains(word.upper())}")
        assert gaddag.contains(word.upper())

def test_normalisation(gaddag):
    """Test word normalization."""
    print("\n=== Test de normalisation ===")

    test_cases = [
        ("été", "ETE"),
        ("l'été", "LETE"),
        ("ça va", "CAVA"),
        ("DÉJÀ", "DEJA"),
        ("week-end", "WEEKEND"),
        ("   espaces   ", "ESPACES"),
        ("mélange-d'ACCENTS", "MELANGEDACCENTS"),
        ("œuf", "OEUF"),  # Special case: œ -> OE
    ]

    for input_word, expected in test_cases:
        normalized = gaddag.normalize_word(input_word)
        print(f"'{input_word}' -> '{normalized}' (attendu: '{expected}')")
        assert normalized == expected

def test_skeleton_pattern_matching(gaddag):
    """Test pattern matching using skeleton coordinates."""
    print("\n=== Test de recherche avec squelettes ===")

    test_cases = [
        # Simple patterns
        ({1: 'R', 3: 'P'}, {'R', 'A', 'I'}, []),  # Corrected: No direct match
        ({0: 'T', 4: 'N'}, {'R', 'A', 'I'}, ["TRAIN"]), # This one works
        ({0: 'T', 2: 'O'}, {'R', 'P'}, ["TROP"]), # This one also works

        # No matches
        ({1: 'X', 3: 'P'}, {'R', 'A', 'I'}, []),
        ({0: 'T', 5: 'P'}, {'R', 'A', 'I'}, []),  # Position out of range

        # Edge cases
        ({}, {'A', 'B', 'C'}, []),  # Empty skeleton
        ({0: 'Z'}, {'A', 'B', 'C'}, [])  # No words with Z
    ]

    for skeleton, available, expected in test_cases:
        found = gaddag.find_words_with_skeleton(skeleton, available)
        print(f"\nPattern: {skeleton}")
        print(f"Available: {available}")
        print(f"Found: {found}")
        print(f"Expected: {expected}")
        assert sorted(found) == sorted(expected)

def test_bridge_word_finding(gaddag):
    """Test finding words that bridge between two positions."""
    print("\n=== Test de recherche de mots ponts ===")

    test_cases = [
        # Horizontal bridges
        ((0, 0), 'T', (0, 3), 'P', {'R', 'A', 'I'}, ["TRAP", "TRIP"]),  # Corrected expectation
        ((0, 0), 'S', (0, 3), 'P', {'T', 'E'}, ["STEP"]),
        # Vertical bridges
        ((0, 0), 'S', (3, 0), 'P', {'H', 'I'}, ["SHIP"]),
        # No possible bridges (these remain correct)
        ((0, 0), 'X', (0, 3), 'Y', {'A', 'B', 'C'}, []),
        ((0, 0), 'T', (0, 8), 'P', {'A', 'B', 'C'}, []),  # Too long for any word in test_words.txt
    ]

    for (row1, col1), letter1, (row2, col2), letter2, available, expected in test_cases:
        # Construct the skeleton based on positions.
        skeleton = {}
        if row1 == row2:  # Horizontal
            # The skeleton keys are *relative* positions within the potential word.
            #  We don't care about the absolute row/col on a hypothetical board.
            min_col = min(col1, col2)
            skeleton[col1 - min_col] = letter1.upper()
            skeleton[col2 - min_col] = letter2.upper()
        elif col1 == col2:  # Vertical
            min_row = min(row1, row2)
            skeleton[row1 - min_row] = letter1.upper()
            skeleton[row2 - min_row] = letter2.upper()
        else:
            continue  # Should not happen, as per your original code.

        found = gaddag.find_words_with_skeleton(skeleton, available)
        print(f"\nBridge from {letter1}@({row1},{col1}) to {letter2}@({row2},{col2})")
        print(f"Available: {available}")
        print(f"Skeleton: {skeleton}")  # Print the constructed skeleton
        print(f"Found: {found}")
        print(f"Expected: {expected}")
        assert sorted(found) == sorted(expected)