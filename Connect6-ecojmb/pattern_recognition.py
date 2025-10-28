"""
Professional Pattern Recognition for Connect 6
Includes threat space search and tactical pattern database
"""

from defines import *
from collections import defaultdict


class ThreatPattern:
    """Represents a threat pattern in Connect 6."""

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
    """
    Professional pattern recognition system.
    Detects tactical patterns, threats, and formations.
    """

    def __init__(self):
        # Pattern weights for evaluation
        self.pattern_scores = {
            # Winning patterns
            'SIX_IN_ROW': 10000000,
            'FIVE_IN_ROW': 5000000,

            # Critical threats (level 5)
            'OPEN_FOUR': 5000000,      # OOOO with both ends open
            'DOUBLE_FOUR': 800000,     # Two fours at once (unstoppable)

            # Strong threats (level 4)
            'STRAIGHT_FOUR': 2000000,   # OOOO with one end open
            'FOUR_THREE': 400000,      # Four + Three combination

            # Medium threats (level 3)
            'OPEN_THREE': 200000,       # OOO with both ends open
            'DOUBLE_THREE': 80000,     # Two threes at once

            # Weak threats (level 2)
            'STRAIGHT_THREE': 5000,    # OOO with one end blocked
            'OPEN_TWO': 1000,          # OO with space to extend

            # Positional patterns (level 1)
            'SPLIT_THREE': 500,        # O_O or O__O patterns
            'LOOSE_TWO': 100,

            # Formations
            'DIAMOND': 2000,           # Diamond formation
            'SQUARE': 1500,            # 2x2 square
            'BRIDGE': 800,             # Bridge connection
        }

        self.directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    def analyze_position(self, board, color):
        """
        Deep analysis of position for given color.

        Returns:
            {
                'threats': [ThreatPattern],
                'score': int,
                'critical_level': int (0-5),
                'winning_moves': [(x, y)],
                'defensive_moves': [(x, y)]
            }
        """
        threats = []
        winning_moves = []
        defensive_moves = []
        total_score = 0
        max_threat_level = 0

        # Find all threats for this color
        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] == color:
                    # Check each direction
                    for direction in self.directions:
                        threat = self._analyze_line(
                            board, x, y, direction, color)
                        if threat:
                            threats.append(threat)
                            total_score += self.pattern_scores.get(
                                threat.pattern_type, 0)
                            max_threat_level = max(
                                max_threat_level, threat.threat_level)

                            if threat.threat_level >= 5:
                                winning_moves.extend(threat.win_positions)
                            elif threat.threat_level >= 4:
                                defensive_moves.extend(threat.win_positions)

        # Remove duplicate winning moves
        winning_moves = list(set(winning_moves))
        defensive_moves = list(set(defensive_moves))

        return {
            'threats': threats,
            'score': total_score,
            'critical_level': max_threat_level,
            'winning_moves': winning_moves,
            'defensive_moves': defensive_moves
        }

    def _analyze_line(self, board, x, y, direction, color):
        """
        Analyze a line starting from (x, y) in given direction.
        Returns ThreatPattern if found, None otherwise.
        """
        dx, dy = direction

        # Count consecutive stones
        consecutive = 1
        temp_x, temp_y = x + dx, y + dy

        while (1 <= temp_x <= 19 and 1 <= temp_y <= 19 and
               board[temp_x][temp_y] == color):
            consecutive += 1
            temp_x += dx
            temp_y += dy

        # Only analyze if we have at least 2 in a row
        if consecutive < 2:
            return None

        # Find the full extent of the line
        start_x, start_y = x, y
        temp_x, temp_y = x - dx, y - dy
        while (1 <= temp_x <= 19 and 1 <= temp_y <= 19 and
               board[temp_x][temp_y] == color):
            start_x, start_y = temp_x, temp_y
            temp_x -= dx
            temp_y -= dy

        # Get positions
        positions = []
        for i in range(consecutive):
            positions.append((start_x + i * dx, start_y + i * dy))

        # Check spaces before and after
        before_x = start_x - dx
        before_y = start_y - dy
        after_x = start_x + consecutive * dx
        after_y = start_y + consecutive * dy

        before_open = (1 <= before_x <= 19 and 1 <= before_y <= 19 and
                       board[before_x][before_y] == Defines.NOSTONE)
        after_open = (1 <= after_x <= 19 and 1 <= after_y <= 19 and
                      board[after_x][after_y] == Defines.NOSTONE)

        # Classify pattern
        pattern_type, threat_level = self._classify_threat(
            consecutive, before_open, after_open
        )

        # Find winning positions
        win_positions = []
        if before_open:
            win_positions.append((before_x, before_y))
        if after_open:
            win_positions.append((after_x, after_y))

        # Check for extensions with gaps (e.g., OOOO or OOO_O)
        if after_open and consecutive >= 3:
            # Check for one-gap extension
            gap_x = after_x + dx
            gap_y = after_y + dy
            if (1 <= gap_x <= 19 and 1 <= gap_y <= 19 and
                    board[gap_x][gap_y] == color):
                win_positions.append((after_x, after_y))

        if pattern_type:
            return ThreatPattern(pattern_type, positions, threat_level, win_positions)

        return None

    def _classify_threat(self, length, before_open, after_open):
        """
        Classify threat based on length and openness.

        Returns: (pattern_type, threat_level)
        """
        both_open = before_open and after_open
        one_open = before_open or after_open

        if length >= 6:
            return 'SIX_IN_ROW', 5

        elif length == 5:
            return 'FIVE_IN_ROW', 5

        elif length == 4:
            if both_open:
                return 'OPEN_FOUR', 5  # Unstoppable
            elif one_open:
                return 'STRAIGHT_FOUR', 4
            else:
                return None, 0  # Blocked on both ends

        elif length == 3:
            if both_open:
                return 'OPEN_THREE', 3
            elif one_open:
                return 'STRAIGHT_THREE', 2
            else:
                return None, 0

        elif length == 2:
            if both_open:
                return 'OPEN_TWO', 2
            elif one_open:
                return 'LOOSE_TWO', 1
            else:
                return None, 0

        return None, 0

    def find_threat_combinations(self, board, color):
        """
        Find combinations of threats (double threats, etc.).
        These are often game-winning.
        """
        analysis = self.analyze_position(board, color)
        threats = analysis['threats']

        combinations = []

        # Check for double fours (two four-in-a-rows)
        fours = [t for t in threats if t.threat_level >= 4]
        if len(fours) >= 2:
            # Check if they share winning positions (true double threat)
            winning_sets = [set(t.win_positions) for t in fours]
            shared = set.intersection(*winning_sets) if winning_sets else set()

            if shared:
                combinations.append({
                    'type': 'DOUBLE_FOUR',
                    'score': 900000,
                    'moves': list(shared)
                })

        # Check for four + three combination
        threes = [t for t in threats if t.threat_level == 3]
        if fours and threes:
            # Any position that creates both is winning
            four_wins = set()
            for f in fours:
                four_wins.update(f.win_positions)

            three_wins = set()
            for t in threes:
                three_wins.update(t.win_positions)

            shared = four_wins & three_wins
            if shared:
                combinations.append({
                    'type': 'FOUR_THREE',
                    'score': 400000,
                    'moves': list(shared)
                })

        # Check for double three (two open threes)
        open_threes = [t for t in threats if t.pattern_type == 'OPEN_THREE']
        if len(open_threes) >= 2:
            winning_sets = [set(t.win_positions) for t in open_threes]
            shared = set.intersection(*winning_sets) if winning_sets else set()

            if shared:
                combinations.append({
                    'type': 'DOUBLE_THREE',
                    'score': 80000,
                    'moves': list(shared)
                })

        return combinations

    def detect_formations(self, board, color):
        """
        Detect special formations (square, diamond, bridge, etc.).
        """
        formations = []

        # Check for 2x2 squares
        for x in range(1, 19):
            for y in range(1, 19):
                if (board[x][y] == color and
                    board[x+1][y] == color and
                    board[x][y+1] == color and
                        board[x+1][y+1] == color):

                    formations.append({
                        'type': 'SQUARE',
                        'positions': [(x, y), (x+1, y), (x, y+1), (x+1, y+1)],
                        'score': self.pattern_scores['SQUARE']
                    })

        # Check for diamond formations
        for x in range(2, 18):
            for y in range(2, 18):
                if (board[x][y] == color and
                    board[x-1][y] == color and
                    board[x+1][y] == color and
                    board[x][y-1] == color and
                        board[x][y+1] == color):

                    formations.append({
                        'type': 'DIAMOND',
                        'positions': [(x, y), (x-1, y), (x+1, y), (x, y-1), (x, y+1)],
                        'score': self.pattern_scores['DIAMOND']
                    })

        return formations

    def evaluate_tactical_score(self, board, color):
        """
        Complete tactical evaluation using pattern recognition.
        """
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

        # Weight opponent threats more heavily (defensive play)
        total = our_score - opp_score * 3.0

        return int(total), our_analysis, opp_analysis
