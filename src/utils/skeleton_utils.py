"""Utilities for generating bridge skeletons between pattern coordinates."""

from typing import Set, Tuple

def generate_bridge_skeletons(pattern: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    """Generate bridge skeleton coordinates between pattern coordinates.
    
    Args:
        pattern: Set of (x, y) coordinate tuples representing the pattern
        
    Returns:
        Set of (x, y) coordinate tuples for bridge positions
        
    Raises:
        ValueError: If pattern is empty or has fewer than 2 coordinates
        ValueError: If pattern coordinates are not connected
        TypeError: If coordinates are not tuples or contain non-integer values
    """
    # Input validation
    if not pattern:
        raise ValueError("Pattern cannot be empty")
    
    if len(pattern) < 2:
        raise ValueError("Pattern must contain at least 2 coordinates")
    
    # Validate all coordinates are integer tuples
    for coord in pattern:
        if not isinstance(coord, tuple):
            raise TypeError("All coordinates must be tuples")
        if len(coord) != 2:
            raise TypeError("Coordinates must be 2D tuples")
        if not all(isinstance(n, int) for n in coord):
            raise TypeError("Coordinates must contain only integers")

    # Check if pattern is connected
    remaining = set(pattern)
    connected = {next(iter(remaining))}  # Start with first coordinate
    remaining.remove(next(iter(remaining)))
    
    while remaining and any(
        abs(x1 - x2) + abs(y1 - y2) == 1  # Manhattan distance = 1
        for x1, y1 in connected
        for x2, y2 in remaining
    ):
        newly_connected = {
            (x2, y2) for x2, y2 in remaining
            if any(abs(x1 - x2) + abs(y1 - y2) == 1 for x1, y1 in connected)
        }
        connected.update(newly_connected)
        remaining.difference_update(newly_connected)
    
    if remaining:
        raise ValueError("Pattern must be connected")

    # Find potential bridge positions
    bridges = set()
    
    # Get pattern bounds
    xs = [x for x, _ in pattern]
    ys = [y for _, y in pattern]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    # Check each potential bridge position
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            if (x, y) in pattern:
                continue
            
            # Count orthogonally adjacent pattern tiles
            adjacent = 0
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if (x + dx, y + dy) in pattern:
                    adjacent += 1
            
            # Position is a bridge if it has at least 2 orthogonally adjacent pattern tiles
            if adjacent >= 2:
                bridges.add((x, y))

    return bridges