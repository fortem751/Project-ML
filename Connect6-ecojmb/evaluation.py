"""
Professional Evaluation Function for Connect 6
Integrates pattern recognition, threat analysis, and positional understanding
"""

from defines import *
from pattern_recognition import PatternRecognizer


class Evaluator:
    """Professional-grade position evaluator."""

    def __init__(self):
        # Initialize pattern recognizer
        self.pattern_recognizer = PatternRecognizer()

        # Core evaluation weights (refined through testing)
        self.weights = {
            # Material/Tactical (most important)
            'win': 10000000,
            'pattern_score': 1.0,      # Use pattern recognizer scores directly

            # Positional factors
            'center_control': 8,
            'mobility': 3,
            'connectivity': 5,
            'influence': 4,

            # Strategic
            'tempo': 10,
            'development': 6,
        }

        # Evaluation cache for performance
        self.eval_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def evaluate_position(self, board, color):
        """
        Master evaluation function.
        Combines tactical, positional, and strategic factors.
        """
        # Check for immediate game-ending positions first
        if self._is_won(board, color):
            return Defines.MAXINT - 1

        opponent = Defines.BLACK if color == Defines.WHITE else Defines.WHITE
        if self._is_won(board, opponent):
            return Defines.MININT + 1

        # Tactical evaluation (patterns and threats)
        tactical_score, our_analysis, opp_analysis = \
            self.pattern_recognizer.evaluate_tactical_score(board, color)

        # Positional evaluation
        positional_score = self._evaluate_positional(board, color)

        # Strategic evaluation
        strategic_score = self._evaluate_strategic(
            board, color, our_analysis, opp_analysis)

        # Combine scores
        total = tactical_score + positional_score + strategic_score

        # Bonus for having the initiative (higher critical level)
        if our_analysis['critical_level'] > opp_analysis['critical_level']:
            total += 5000 * \
                (our_analysis['critical_level'] -
                 opp_analysis['critical_level'])

        return int(total)

    def _is_won(self, board, color):
        """Quick check if color has won."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] == color:
                    for dx, dy in directions:
                        count = 1
                        tx, ty = x + dx, y + dy
                        while (1 <= tx <= 19 and 1 <= ty <= 19 and
                               board[tx][ty] == color):
                            count += 1
                            tx += dx
                            ty += dy
                            if count >= 6:
                                return True

                        tx, ty = x - dx, y - dy
                        while (1 <= tx <= 19 and 1 <= ty <= 19 and
                               board[tx][ty] == color):
                            count += 1
                            tx -= dx
                            ty -= dy
                            if count >= 6:
                                return True

        return False

    def _evaluate_positional(self, board, color):
        """
        Evaluate positional factors:
        - Center control
        - Mobility
        - Connectivity
        - Influence
        """
        score = 0
        opponent = Defines.BLACK if color == Defines.WHITE else Defines.WHITE

        # Center control (stones near center are more valuable)
        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] == color:
                    distance = abs(x - 10) + abs(y - 10)
                    score += self.weights['center_control'] * (20 - distance)
                elif board[x][y] == opponent:
                    distance = abs(x - 10) + abs(y - 10)
                    score -= self.weights['center_control'] * \
                        (20 - distance) * 0.5

        # Mobility (number of adjacent empty squares)
        our_mobility = 0
        opp_mobility = 0

        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] == color:
                    our_mobility += self._count_adjacent_empty(board, x, y)
                elif board[x][y] == opponent:
                    opp_mobility += self._count_adjacent_empty(board, x, y)

        score += (our_mobility - opp_mobility * 0.8) * self.weights['mobility']

        # Connectivity (stones connected to each other)
        our_connectivity = self._count_connectivity(board, color)
        opp_connectivity = self._count_connectivity(board, opponent)
        score += (our_connectivity - opp_connectivity) * \
            self.weights['connectivity']

        # Influence (control of key areas)
        our_influence = self._calculate_influence(board, color)
        opp_influence = self._calculate_influence(board, opponent)
        score += (our_influence - opp_influence) * self.weights['influence']

        return score

    def _count_adjacent_empty(self, board, x, y):
        """Count empty squares adjacent to (x, y)."""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (1 <= nx <= 19 and 1 <= ny <= 19 and
                        board[nx][ny] == Defines.NOSTONE):
                    count += 1
        return count

    def _count_connectivity(self, board, color):
        """
        Count connections between stones.
        Stones within distance 2 are considered connected.
        """
        stones = []
        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] == color:
                    stones.append((x, y))

        connections = 0
        for i, (x1, y1) in enumerate(stones):
            for x2, y2 in stones[i+1:]:
                dist = abs(x1 - x2) + abs(y1 - y2)
                if dist <= 3:
                    connections += (4 - dist)  # Closer = better

        return connections

    def _calculate_influence(self, board, color):
        """
        Calculate influence/territorial control.
        Each stone radiates influence to nearby squares.
        """
        influence_map = [[0] * 21 for _ in range(21)]

        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] == color:
                    # Radiate influence
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            nx, ny = x + dx, y + dy
                            if 1 <= nx <= 19 and 1 <= ny <= 19:
                                dist = abs(dx) + abs(dy)
                                if dist <= 5:
                                    influence_map[nx][ny] += (6 - dist)

        # Sum up influence in unoccupied squares
        total_influence = 0
        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] == Defines.NOSTONE:
                    total_influence += influence_map[x][y]

        return total_influence

    def _evaluate_strategic(self, board, color, our_analysis, opp_analysis):
        """
        Evaluate strategic factors:
        - Tempo (who is attacking)
        - Development (number of active stones)
        """
        score = 0

        # Tempo: reward for having more/better threats
        threat_advantage = len(
            our_analysis['threats']) - len(opp_analysis['threats'])
        score += threat_advantage * self.weights['tempo']

        # Development: number of stones involved in threats
        our_development = len(set(
            pos for threat in our_analysis['threats']
            for pos in threat.positions
        ))

        opp_development = len(set(
            pos for threat in opp_analysis['threats']
            for pos in threat.positions
        ))

        score += (our_development - opp_development) * \
            self.weights['development']

        return score

    # ===== Tactical Analysis Methods =====

    def detect_immediate_win(self, board, color):
        """Find all winning moves (places 6th stone)."""
        analysis = self.pattern_recognizer.analyze_position(board, color)
        return analysis['winning_moves']

    def detect_immediate_threat(self, board, color):
        """Detect if opponent can win."""
        opponent = Defines.BLACK if color == Defines.WHITE else Defines.WHITE
        return self.detect_immediate_win(board, opponent)

    def detect_critical_moves(self, board, color):
        """
        Find moves that create critical threats (fours, open threes).
        Returns list of (position, threat_level, score).
        """
        critical_moves = []

        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] == Defines.NOSTONE:
                    # Try placing stone
                    board[x][y] = color

                    analysis = self.pattern_recognizer.analyze_position(
                        board, color)

                    # If creates critical threat, record it
                    if analysis['critical_level'] >= 3:
                        critical_moves.append({
                            'position': (x, y),
                            'threat_level': analysis['critical_level'],
                            'score': analysis['score']
                        })

                    board[x][y] = Defines.NOSTONE

        # Sort by threat level and score
        critical_moves.sort(key=lambda m: (
            m['threat_level'], m['score']), reverse=True)

        return critical_moves

    def find_forcing_moves(self, board, color):
        """
        Find forcing moves (moves opponent must respond to).
        """
        forcing = []

        critical = self.detect_critical_moves(board, color)

        # Any move creating threat level 4+ is forcing
        for move in critical:
            if move['threat_level'] >= 4:
                forcing.append(move['position'])

        return forcing

    def get_threat_analysis(self, board, color):
        """
        Complete threat analysis for a position.
        Returns detailed information about all threats.
        """
        our_analysis = self.pattern_recognizer.analyze_position(board, color)

        opponent = Defines.BLACK if color == Defines.WHITE else Defines.WHITE
        opp_analysis = self.pattern_recognizer.analyze_position(
            board, opponent)

        our_combos = self.pattern_recognizer.find_threat_combinations(
            board, color)
        opp_combos = self.pattern_recognizer.find_threat_combinations(
            board, opponent)

        return {
            'our_analysis': our_analysis,
            'opp_analysis': opp_analysis,
            'our_combinations': our_combos,
            'opp_combinations': opp_combos,
            'critical_situation': (
                our_analysis['critical_level'] >= 4 or
                opp_analysis['critical_level'] >= 4
            )
        }

    def clear_cache(self):
        """Clear evaluation cache."""
        self.eval_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0

    def get_cache_stats(self):
        """Get cache statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0

        return {
            'size': len(self.eval_cache),
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': hit_rate * 100
        }
