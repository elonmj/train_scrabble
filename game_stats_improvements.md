# GameStats Implementation Improvements

## Current Implementation Analysis

The current GameStats implementation has several areas that need improvement:

1. Direction Detection
2. Bingo Detection
3. Board State Tracking
4. Input Validation
5. Error Handling

## Detailed Improvements

### 1. Direction Detection

Current issue: Direction is hardcoded to HORIZONTAL.

Solution: Implement direction detection by:
- Adding a new method to determine direction from position format
- Using Board's coordinate parsing capabilities
- Considering both H8/8H format support

```python
def _determine_direction(self, position: str) -> Direction:
    """
    Determine word direction from the position format.
    Examples: 
    - H8 -> HORIZONTAL (letter then number)
    - 8H -> VERTICAL (number then letter)
    """
    first_char = position[0].upper()
    if first_char.isalpha():
        return Direction.HORIZONTAL
    return Direction.VERTICAL
```

### 2. Bingo Detection

Current issue: Only counts 7-letter words as bingos.

Solution: Enhance bingo detection by:
- Tracking tiles placed vs existing tiles
- Using Board state to verify actual tile placement
- Counting connecting words correctly

```python
def _is_bingo(self, position: str, word: str, direction: Direction) -> bool:
    """
    Check if move is a bingo by counting newly placed tiles.
    A bingo requires placing exactly 7 tiles in one turn.
    """
    row, col = self.board.parse_coordinates(position)
    tiles_placed = 0
    
    for i, letter in enumerate(word):
        curr_row = row + (i if direction == Direction.VERTICAL else 0)
        curr_col = col + (i if direction == Direction.HORIZONTAL else 0)
        if not self.board.get_letter(curr_row, curr_col):
            tiles_placed += 1
            
    return tiles_placed == 7
```

### 3. Board State Tracking

Current issue: Board state isn't updated after moves.

Solution: Track board state by:
- Updating board after each move
- Using Board's place_letter method
- Managing multiplier usage

```python
def _update_board_state(self, position: str, word: str, direction: Direction) -> None:
    """Update board state with played word."""
    row, col = self.board.parse_coordinates(position)
    
    for i, letter in enumerate(word):
        curr_row = row + (i if direction == Direction.VERTICAL else 0)
        curr_col = col + (i if direction == Direction.HORIZONTAL else 0)
        self.board.place_letter(curr_row, curr_col, letter)
```

### 4. Input Validation

Current issue: Limited validation of moves and positions.

Solution: Add comprehensive validation:
- Position format validation
- Board boundary checks
- Move format validation

```python
def _validate_move(self, position: str, word: str) -> bool:
    """
    Validate move format and board position.
    Returns True if valid, False otherwise.
    """
    try:
        # Validate position format and boundaries
        row, col = self.board.parse_coordinates(position)
        direction = self._determine_direction(position)
        
        # Validate word fits on board
        if direction == Direction.HORIZONTAL:
            if col + len(word) > self.board.SIZE:
                return False
        else:
            if row + len(word) > self.board.SIZE:
                return False
                
        return True
        
    except ValueError:
        return False
```

### 5. Error Handling

Current issue: Missing error handling for edge cases.

Solution: Add error handling for:
- Invalid move formats
- Out of bounds positions
- Malformed input lines
- Invalid multiplier usage

```python
class GameStatsError(Exception):
    """Base exception for GameStats errors."""
    pass

class InvalidMoveError(GameStatsError):
    """Raised when a move is invalid."""
    pass

class InvalidPositionError(GameStatsError):
    """Raised when a position is invalid."""
    pass
```

## Integration Plan

1. Update class initialization:
   - Initialize error classes
   - Set up board state tracking
   - Add validation flags

2. Enhance move parsing:
   - Add input validation
   - Implement direction detection
   - Update board state
   - Track multiplier usage

3. Improve bingo detection:
   - Count actual tiles placed
   - Consider connecting words
   - Validate against board state

4. Add error handling:
   - Wrap critical operations in try/catch
   - Provide meaningful error messages
   - Log validation failures

## Testing Strategy

1. Test move parsing:
   - Valid/invalid positions
   - Different word lengths
   - Edge cases (board boundaries)

2. Test bingo detection:
   - 7-letter words
   - Connecting plays
   - Multiple word formations

3. Test board state:
   - Multiplier tracking
   - Letter placement
   - Move history

4. Test error handling:
   - Invalid input formats
   - Out of bounds plays
   - Malformed data

## Next Steps

1. Create unit tests for new functionality
2. Implement improvements in Code mode
3. Validate against game rules
4. Test with real game data