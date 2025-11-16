
from defines import *
from collections import defaultdict
from typing import List, Dict, Tuple


class ThreatPattern:

    def __init__(self, pattern_type, positions, threat_level, win_positions):
        """
        Args:
            pattern_type: Type of threat (e.g., "OPEN_FOUR", "STRAIGHT_FOUR")
            positions: List of (x, y) occupied positions
            threat_level: Urgency (0-5, where 5 is immediate win)
            win_positions: List of (x, y) positions that complete the threat
        """
        self.pattern_type = pattern_type
        self.positions = positions
        self.threat_level = threat_level
        self.win_positions = win_positions


class PatternRecognizer:

    def __init__(self):
        # Pattern weights for evaluation
        self.pattern_scores = {
            # Winning patterns
            'SIX_IN_ROW': 10000000,
            'FIVE_IN_ROW': 5000000,

            # Critical threats (level 5)
            'OPEN_FOUR': 5000000,      # OOOO with both ends open
            'DOUBLE_FOUR': 1000000,
            'pattern_4_open': 10000.0,
            'threat_win_immediate': 1000000.0,


            'pattern_score': 1.0,
        }

    def update_pattern_scores(self, new_weights: Dict[str, float]):

        self.pattern_scores.update(new_weights)

    def _get_adjacent_empty_positions(self, board) -> List[Tuple[int, int]]:

        candidates = set()

        # Search the 19x19 playable area
        for x in range(1, Defines.GRID_NUM - 1):
            for y in range(1, Defines.GRID_NUM - 1):
                if board[x][y] != Defines.NOSTONE:
                    # Found a stone, check its 8 neighbors
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue

                            nx, ny = x + dx, y + dy

                            # Check if neighbor is on the board and is empty
                            if 1 <= nx <= 19 and 1 <= ny <= 19 and board[nx][ny] == Defines.NOSTONE:
                                candidates.add((nx, ny))

        return list(candidates)

    def _check_win_at(self, board, x, y, color):

        # Check four directions: Horizontal, Vertical, Diagonal (\), Anti-Diagonal (/)
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            count = 1  # The stone at (x, y)

            # Count forward
            cx, cy = x + dx, y + dy
            while (1 <= cx <= 19 and 1 <= cy <= 19 and board[cx][cy] == color):
                count += 1
                cx += dx
                cy += dy

            # Count backward
            cx, cy = x - dx, y - dy
            while (1 <= cx <= 19 and 1 <= cy <= 19 and board[cx][cy] == color):
                count += 1
                cx -= dx
                cy -= dy

            if count >= 6:
                return True
        return False

    def find_winning_moves(self, board, color) -> List[Tuple[int, int]]:

        winning_moves = []

        # Only check open positions near existing stones (heuristic for speed)
        candidate_moves = self._get_adjacent_empty_positions(board)

        for x, y in candidate_moves:
            if board[x][y] == Defines.NOSTONE:
                # Temporarily place a stone
                board[x][y] = color

                # Check if this single placement creates a 6-in-a-row
                if self._check_win_at(board, x, y, color):
                    winning_moves.append((x, y))

                # Unmake the move (CRITICAL)
                board[x][y] = Defines.NOSTONE

        return winning_moves

    def is_six_in_a_row(self, board, color) -> bool:

        # Simple implementation for win check after move
        for x in range(1, Defines.GRID_NUM - 1):
            for y in range(1, Defines.GRID_NUM - 1):
                if board[x][y] == color:
                    # Check win at EVERY stone on the board for simplicity
                    if self._check_win_at(board, x, y, color):
                        return True
        return False

    def analyze_position(self, board, color):

        return {'score': 0, 'critical_level': 0}

    def find_threat_combinations(self, board, color):

        return []

    def detect_formations(self, board, color):

        return []

    def evaluate_tactical_score(self, board, color):

        # Our threats
        our_analysis = self.analyze_position(board, color)
        our_combinations = self.find_threat_combinations(board, color)
        our_formations = self.detect_formations(board, color)

        # Opponent threats
        opponent = Defines.BLACK if color == Defines.WHITE else Defines.WHITE
        opp_analysis = self.analyze_position(board, opponent)
        opp_combinations = self.find_threat_combinations(board, opponent)

        # Calculate score
        our_score = our_analysis['score']
        our_score += sum(c['score'] for c in our_combinations)
        our_score += sum(f['score'] for f in our_formations)

        opp_score = opp_analysis['score']
        opp_score += sum(c['score'] for c in opp_combinations)

        return our_score - opp_score
