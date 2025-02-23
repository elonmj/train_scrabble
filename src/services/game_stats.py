from typing import Dict, List, Tuple, Optional
import re
from statistics import median
from ..models.board import Board
from ..models.types import Direction, SquareType

class GameStats:
    """Analyzes game statistics from ISC move lists."""
    
    # Letters worth 10 points in French Scrabble
    HIGH_VALUE_LETTERS = set('QZKWXY')
    
    def __init__(self):
        self.board = Board()  # For tracking multiplier usage
        
        # Initialize statistics containers
        self.players = {'player1': None, 'player2': None}  # Will store player names
        self.ratings = {'player1': None, 'player2': None}  # Will store player ratings
        
        # Per-player statistics
        self.scores = {'player1': [], 'player2': []}  # List of scores per move
        self.total_scores = {'player1': 0, 'player2': 0}  # Final scores
        self.moves = {'player1': [], 'player2': []}  # List of all moves
        
        # Special moves
        self.passes = {'player1': 0, 'player2': 0}
        self.changes = {'player1': 0, 'player2': 0}
        
        # Bingo tracking
        self.bingos = {'player1': [], 'player2': []}  # List of (word, score) tuples
        
        # High-value letter plays
        self.high_value_plays = {'player1': [], 'player2': []}  # List of (word, letter, position) tuples
        
        # Multiplier plays
        self.quadruples = {'player1': [], 'player2': []}  # Two double word squares
        self.nonuples = {'player1': [], 'player2': []}    # Two triple word squares
        self.legendres = {'player1': [], 'player2': []}   # 10-pt letter on multiplier

    def parse_move_list(self, move_list: str) -> None:
        """Parse a complete ISC move list and compute all statistics."""
        lines = move_list.splitlines()
        
        # Parse first line with ratings
        self._parse_ratings_line(lines[0])
        
        # Parse moves until we hit the final score line
        current_line = 1
        while current_line < len(lines):
            line = lines[current_line].strip()
            if not line:
                current_line += 1
                continue
                
            if 'points' in line:  # Final score line
                self._parse_final_score(line)
                break
                
            # Parse regular move line
            if '.' in line:  # Move numbers start with "1.", "2.", etc.
                self._parse_move_line(line)
            current_line += 1

    def _parse_ratings_line(self, line: str) -> None:
        """Parse line with player names and ratings: (734)20067s         (859)joselonm"""
        pattern = r'\((\d+)\)(\w+)'
        matches = re.findall(pattern, line)
        if len(matches) >= 2:
            self.ratings['player1'] = int(matches[0][0])
            self.players['player1'] = matches[0][1]
            self.ratings['player2'] = int(matches[1][0])
            self.players['player2'] = matches[1][1]

    def _parse_move_line(self, line: str) -> None:
        """Parse a move line: 1. CHANGE 6         H2 sucates 74"""
        parts = line.split()
        
        # Skip move number
        move_parts = parts[1:]
        
        # Parse player 1's move
        next_idx = self._parse_single_move(move_parts, 'player1')
        
        # If there are more parts, parse player 2's move
        if next_idx < len(move_parts):
            self._parse_single_move(move_parts[next_idx:], 'player2')

    def _parse_single_move(self, parts: List[str], player: str) -> int:
        """Parse one player's move and update statistics. Returns number of parts consumed."""
        if parts[0] == 'PASS':
            self.passes[player] += 1
            return 1
            
        if parts[0] == 'CHANGE':
            self.changes[player] += 1
            return 2  # Consume CHANGE and the number of letters
            
        # Regular move: H2 sucates 74
        position = parts[0]
        word = parts[1]
        score = int(parts[2])
        
        # Update basic stats
        self.scores[player].append(score)
        self.moves[player].append((position, word, score))
        
        # Check for bingo (exactly 7 letters placed)
        if len(word) == 7:  # Only count 7-letter words as bingos
            self.bingos[player].append((word, score))
            
        # Check for high-value letters (case insensitive)
        for letter in word.upper():  # Convert to upper case for comparison
            if letter in self.HIGH_VALUE_LETTERS:
                self.high_value_plays[player].append((word, letter, position))
                
        # Analyze board position for multipliers
        self._analyze_multipliers(position, word, player)
        
        return 3  # Consumed 3 parts: position, word, score

    def _analyze_multipliers(self, position: str, word: str, player: str) -> None:
        """Analyze a move for multiplier usage (quadruples, nonuples, legendres)."""
        # Convert position (e.g. 'H2' or '6F') to row, col
        first_char = position[0].upper()
        if first_char.isalpha():
            # Format: H2 (letter then number)
            row = ord(first_char) - ord('A')
            col = int(position[1:]) - 1
        else:
            # Format: 6F (number then letter)
            row = ord(position[-1].upper()) - ord('A')
            col = int(position[:-1]) - 1
        
        # Determine word direction based on next position
        direction = Direction.HORIZONTAL  # Default, would need to detect from next position
        
        # Track multipliers used in this word
        double_words = 0
        triple_words = 0
        legendres_found = False
        
        # Check each square the word covers
        for i, letter in enumerate(word):
            curr_row = row + (i if direction == Direction.VERTICAL else 0)
            curr_col = col + (i if direction == Direction.HORIZONTAL else 0)
            
            square_type = self.board.get_square_type(curr_row, curr_col)
            
            # Track word multipliers
            if square_type == SquareType.DOUBLE_WORD:
                double_words += 1
            elif square_type == SquareType.TRIPLE_WORD:
                triple_words += 1
                
            # Check for Legendres (10-point letter on multiplier)
            if letter in self.HIGH_VALUE_LETTERS:
                if (square_type == SquareType.DOUBLE_LETTER or 
                    square_type == SquareType.TRIPLE_LETTER):
                    legendres_found = True
        
        # Record multiplier achievements
        if double_words >= 2:
            self.quadruples[player].append((word, position))
        if triple_words >= 2:
            self.nonuples[player].append((word, position))
        if legendres_found:
            self.legendres[player].append((word, position))

    def _parse_final_score(self, line: str) -> None:
        """Parse the final score line: 284 points          332 points"""
        scores = re.findall(r'(\d+)\s+points', line)
        if len(scores) >= 2:
            self.total_scores['player1'] = int(scores[0])
            self.total_scores['player2'] = int(scores[1])

    def _calculate_median_score(self, scores: List[int]) -> float:
        """Calculate median score, excluding PASS and CHANGE moves."""
        if not scores:
            return 0
        return median(scores)

    def get_statistics(self) -> Dict:
        """Return computed statistics for both players."""
        stats = {}
        for player in ['player1', 'player2']:
            # Calculate average and median excluding PASS moves (they have no score)
            scoring_moves = len(self.scores[player])  # Only includes moves with scores
            total_score = sum(self.scores[player])
            median_score = self._calculate_median_score(self.scores[player])
            stats[player] = {
                'player_name': self.players[player],
                'rating': self.ratings[player],
                'total_score': self.total_scores[player],
                'average_score': (total_score / scoring_moves) if scoring_moves > 0 else 0,
                'median_score': median_score,
                'highest_score': max(self.scores[player]) if self.scores[player] else 0,
                'bingos': {
                    'count': len(self.bingos[player]),
                    'words': [f"{word} ({score}pts)" for word, score in self.bingos[player]]
                },
                'special_moves': {
                    'passes': self.passes[player],
                    'changes': self.changes[player]
                },
                'high_value_plays': {
                    'count': len(self.high_value_plays[player]),
                    'details': [f"{word} ({letter} at {pos})" for word, letter, pos in self.high_value_plays[player]]
                },
                'highest_scoring_moves': [
                    f"{move[1]} at {move[0]} ({move[2]}pts)"
                    for move in sorted(self.moves[player], key=lambda x: x[2], reverse=True)[:3]
                ],
                'multiplier_plays': {
                    'quadruples': self.quadruples[player],
                    'nonuples': self.nonuples[player],
                    'legendres': self.legendres[player]
                }
            }
        return stats