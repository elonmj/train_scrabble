
"""Test suite for skeleton generation utilities."""

import pytest
from typing import List, Set, Tuple

from src.utils.skeleton_utils import generate_bridge_skeletons

@pytest.fixture
def pattern_matcher():
    """Fixture to track pattern matching history for debugging."""
    class PatternMatcher:
        def __init__(self):
            self.history = []
            
        def add_match(self, pattern: str, match: Set[Tuple[int, int]]):
            self.history.append((pattern, match))
            
        def get_history(self) -> List[Tuple[str, Set[Tuple[int, int]]]]:
            return self.history
            
    return PatternMatcher()

@pytest.fixture
def assert_skeleton_sets():
    """Fixture for comparing sets of skeleton coordinates."""
    def _assert_equal(actual: Set[Tuple[int, int]], expected: Set[Tuple[int, int]], pattern_matcher):
        pattern_matcher.add_match("actual", actual)
        pattern_matcher.add_match("expected", expected)
        assert actual == expected, f"Skeleton sets don't match:\nActual: {actual}\nExpected: {expected}"
    return _assert_equal

@pytest.fixture
def sample_patterns():
    """Common test patterns."""
    return {
        "empty": set(),
        "single": {(0, 0)},
        "horizontal": {(0, 0), (0, 1), (0, 2)},
        "vertical": {(0, 0), (1, 0), (2, 0)},
        "l_shape": {(0, 0), (1, 0), (1, 1)},
        "t_shape": {(0, 0), (0, 1), (0, 2), (1, 1)},
        "cross": {(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)},
    }

class TestGenerateBridgeSkeletons:
    """Test cases for generate_bridge_skeletons function."""
    
    def test_empty_pattern_raises_error(self):
        """Empty pattern should raise ValueError."""
        with pytest.raises(ValueError) as exc:
            generate_bridge_skeletons(set())
        assert str(exc.value) == "Pattern cannot be empty"

    def test_single_coordinate_raises_error(self):
        """Single coordinate pattern should raise ValueError."""
        with pytest.raises(ValueError) as exc:
            generate_bridge_skeletons({(0, 0)})
        assert str(exc.value) == "Pattern must contain at least 2 coordinates"
    
    def test_disconnected_pattern_raises_error(self, sample_patterns):
        """Disconnected coordinates should raise ValueError."""
        pattern = {(0, 0), (2, 2)}
        with pytest.raises(ValueError) as exc:
            generate_bridge_skeletons(pattern)
        assert str(exc.value) == "Pattern must be connected"
    
    def test_non_tuple_coordinates_raises_error(self):
        """Non-tuple coordinates should raise TypeError."""
        with pytest.raises(TypeError):
            generate_bridge_skeletons({(0, 0), [1, 1]})
    
    def test_invalid_coordinate_type_raises_error(self):
        """Invalid coordinate types should raise TypeError."""
        with pytest.raises(TypeError):
            generate_bridge_skeletons({(0, 0), (1, "1")})
    
    def test_horizontal_line_returns_empty(self, sample_patterns, pattern_matcher, assert_skeleton_sets):
        """Horizontal line pattern should return empty set - no bridges needed."""
        result = generate_bridge_skeletons(sample_patterns["horizontal"])
        assert_skeleton_sets(result, set(), pattern_matcher)
    
    def test_vertical_line_returns_empty(self, sample_patterns, pattern_matcher, assert_skeleton_sets):
        """Vertical line pattern should return empty set - no bridges needed."""
        result = generate_bridge_skeletons(sample_patterns["vertical"])
        assert_skeleton_sets(result, set(), pattern_matcher)
    
    def test_l_shape_returns_bridge(self, sample_patterns, pattern_matcher, assert_skeleton_sets):
        """L-shape pattern should return one bridge coordinate."""
        result = generate_bridge_skeletons(sample_patterns["l_shape"])
        assert_skeleton_sets(result, {(0, 1)}, pattern_matcher)
    
    def test_t_shape_returns_bridges(self, sample_patterns, pattern_matcher, assert_skeleton_sets):
        """T-shape pattern should return bridge coordinates."""
        result = generate_bridge_skeletons(sample_patterns["t_shape"])
        assert_skeleton_sets(result, {(1, 0), (1, 2)}, pattern_matcher)
    
    def test_cross_shape_returns_bridges(self, sample_patterns, pattern_matcher, assert_skeleton_sets):
        """Cross pattern should return bridge coordinates."""
        result = generate_bridge_skeletons(sample_patterns["cross"])
        assert_skeleton_sets(result, {(0, 0), (0, 2), (2, 0), (2, 2)}, pattern_matcher)