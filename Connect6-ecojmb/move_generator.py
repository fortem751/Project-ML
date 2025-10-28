"""
Professional Move Generator for Connect 6
Advanced move ordering and candidate selection
"""

from defines import *
from evaluation import Evaluator


class MoveGenerator:
    """Professional move generator with intelligent pruning."""

    def __init__(self):
        self.evaluator = Evaluator()
        self.move_history = {}  # Track successful moves

    def generate_moves(self, board, color, depth, max_moves=40, pv_move=None):
        """
        Generate ordered list of candidate moves.

        Args:
            board: Current board state
            color: Color to move
            depth: Current search depth
            max_moves: Maximum moves to return
            pv_move: Principal variation move (best from last search)

        Returns:
            List of StoneMove objects, ordered by estimated strength
        """
        opponent = Defines.BLACK if color == Defines.WHITE else Defines.WHITE

        # PRIORITY 0: PV move from transposition table (try first)
        if pv_move:
            moves = [pv_move]
            return moves

        # PRIORITY 1: Can we win immediately?
        our_wins = self.evaluator.detect_immediate_win(board, color)
        if our_wins:
            return self._create_winning_moves(our_wins, board, color)

        # PRIORITY 2: Must defend against immediate loss
        opp_wins = self.evaluator.detect_immediate_win(board, opponent)
        if opp_wins:
            if len(opp_wins) >= 2:
                # Multiple threats - try to block both
                return self._create_desperate_defense(opp_wins, board, color)
            else:
                # Single threat - block and counterattack
                return self._create_defensive_counterattack(
                    opp_wins[0], board, color, max_moves
                )

        # Get threat analysis
        threat_info = self.evaluator.get_threat_analysis(board, color)

        # PRIORITY 3: Critical threats (level 4+)
        if threat_info['critical_situation']:
            return self._generate_critical_moves(board, color, threat_info, max_moves)

        # PRIORITY 4: Standard move generation with smart ordering
        return self._generate_standard_moves(board, color, depth, max_moves)

    def _create_winning_moves(self, win_positions, board, color):
        """Create moves that win immediately."""
        moves = []

        # If multiple wins, use both stones to win
        if len(win_positions) >= 2:
            move = StoneMove()
            move.positions[0].x, move.positions[0].y = win_positions[0]
            move.positions[1].x, move.positions[1].y = win_positions[1]
            move.score = 100000000
            return [move]

        # Single win - use second stone optimally
        win_pos = win_positions[0]

        # Find best second stone placement
        candidates = self.evaluator.detect_critical_moves(board, color)

        for candidate in candidates[:10]:
            if candidate['position'] != win_pos:
                move = StoneMove()
                move.positions[0].x, move.positions[0].y = win_pos
                move.positions[1].x, move.positions[1].y = candidate['position']
                move.score = 100000000 + candidate['score']
                moves.append(move)

        # If no critical moves, place second stone nearby
        if not moves:
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    x2, y2 = win_pos[0] + dx, win_pos[1] + dy
                    if (1 <= x2 <= 19 and 1 <= y2 <= 19 and
                            board[x2][y2] == Defines.NOSTONE and (x2, y2) != win_pos):
                        move = StoneMove()
                        move.positions[0].x, move.positions[0].y = win_pos
                        move.positions[1].x, move.positions[1].y = (x2, y2)
                        move.score = 100000000
                        moves.append(move)
                        if len(moves) >= 10:
                            return moves

        return moves if moves else [self._create_center_move()]

    def _create_desperate_defense(self, threat_positions, board, color):
        """Try to block multiple threats."""
        if len(threat_positions) >= 2:
            move = StoneMove()
            move.positions[0].x, move.positions[0].y = threat_positions[0]
            move.positions[1].x, move.positions[1].y = threat_positions[1]
            move.score = 90000000
            return [move]
        return [self._create_center_move()]

    def _create_defensive_counterattack(self, threat_pos, board, color, max_moves):
        """Block threat and counterattack."""
        moves = []

        # Find our best attacking moves
        our_critical = self.evaluator.detect_critical_moves(board, color)

        # Combine blocking with attacking
        for critical in our_critical[:30]:
            if critical['position'] != threat_pos:
                move = StoneMove()
                move.positions[0].x, move.positions[0].y = threat_pos
                move.positions[1].x, move.positions[1].y = critical['position']

                # Score based on counter-threat level
                move.score = 80000000 + \
                    critical['threat_level'] * 1000000 + critical['score']
                moves.append(move)

        # Sort by score
        moves.sort(key=lambda m: m.score, reverse=True)
        return moves[:max_moves] if moves else [self._create_center_move()]

    def _generate_critical_moves(self, board, color, threat_info, max_moves):
        """Generate moves in critical tactical positions."""
        moves = []

        # Get our critical moves
        our_critical = self.evaluator.detect_critical_moves(board, color)

        # Get opponent's critical moves (we might need to block)
        opponent = Defines.BLACK if color == Defines.WHITE else Defines.opponent
        opp_critical = self.evaluator.detect_critical_moves(board, opponent)

        # Combine attacking and defending
        seen = set()

        # Our attacks
        for move1 in our_critical[:20]:
            pos1 = move1['position']
            if pos1 in seen:
                continue

            # Try combining with other attacks or blocks
            for move2 in our_critical[:15]:
                pos2 = move2['position']
                if pos2 != pos1 and pos2 not in seen:
                    stone_move = StoneMove()
                    stone_move.positions[0].x, stone_move.positions[0].y = pos1
                    stone_move.positions[1].x, stone_move.positions[1].y = pos2

                    score = move1['score'] + move2['score']
                    score += (move1['threat_level'] +
                              move2['threat_level']) * 100000
                    stone_move.score = score

                    moves.append(stone_move)
                    seen.add(pos1)
                    seen.add(pos2)

            # Try combining attack with defense
            for move2 in opp_critical[:10]:
                pos2 = move2['position']
                if pos2 != pos1 and pos2 not in seen:
                    stone_move = StoneMove()
                    stone_move.positions[0].x, stone_move.positions[0].y = pos1
                    stone_move.positions[1].x, stone_move.positions[1].y = pos2

                    score = move1['score'] - move2['score'] * 0.8
                    score += move1['threat_level'] * 100000
                    stone_move.score = score

                    moves.append(stone_move)

        # Sort by score
        moves.sort(key=lambda m: m.score, reverse=True)
        return moves[:max_moves] if moves else self._generate_standard_moves(
            board, color, 0, max_moves
        )

    def _generate_standard_moves(self, board, color, depth, max_moves):
        """Generate moves using standard heuristics."""
        candidate_positions = []
        positions_checked = 0
        max_checks = 400  # Safety limit

        # Collect candidate positions
        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] != Defines.NOSTONE:
                    # Add adjacent empty positions
                    for dx in [-2, -1, 0, 1, 2]:
                        for dy in [-2, -1, 0, 1, 2]:
                            positions_checked += 1
                            if positions_checked > max_checks:
                                break  # Safety exit

                            nx, ny = x + dx, y + dy
                            if (1 <= nx <= 19 and 1 <= ny <= 19 and
                                    board[nx][ny] == Defines.NOSTONE):

                                # Quick evaluation
                                score = self._quick_eval_position(
                                    board, nx, ny, color)
                                candidate_positions.append(((nx, ny), score))

                        if positions_checked > max_checks:
                            break

                    if positions_checked > max_checks:
                        break

            if positions_checked > max_checks:
                break

        # If no stones, use center
        if not candidate_positions:
            for x in range(7, 14):
                for y in range(7, 14):
                    if board[x][y] == Defines.NOSTONE:
                        score = 100 - (abs(x - 10) + abs(y - 10))
                        candidate_positions.append(((x, y), score))

        # Remove duplicates and sort
        unique_candidates = {}
        for pos, score in candidate_positions:
            if pos not in unique_candidates or unique_candidates[pos] < score:
                unique_candidates[pos] = score

        sorted_candidates = sorted(unique_candidates.items(),
                                   key=lambda x: x[1], reverse=True)

        # Take top positions
        top_positions = [
            pos for pos, _ in sorted_candidates[:min(30, len(sorted_candidates))]]

        # Create move combinations
        moves = []
        for i in range(min(15, len(top_positions))):
            for j in range(i + 1, min(20, len(top_positions))):
                move = StoneMove()
                move.positions[0].x, move.positions[0].y = top_positions[i]
                move.positions[1].x, move.positions[1].y = top_positions[j]

                # Score combination
                score1 = unique_candidates[top_positions[i]]
                score2 = unique_candidates[top_positions[j]]

                # Bonus for proximity
                dist = (abs(top_positions[i][0] - top_positions[j][0]) +
                        abs(top_positions[i][1] - top_positions[j][1]))
                proximity_bonus = max(0, 20 - dist * 2)

                move.score = score1 + score2 + proximity_bonus

                # Check history
                move_key = (top_positions[i], top_positions[j])
                if move_key in self.move_history:
                    move.score += self.move_history[move_key]

                moves.append(move)

                if len(moves) >= max_moves:
                    break
            if len(moves) >= max_moves:
                break

        # Sort by score
        moves.sort(key=lambda m: m.score, reverse=True)
        return moves[:max_moves] if moves else [self._create_center_move()]

    def _quick_eval_position(self, board, x, y, color):
        """Quick heuristic evaluation of a position."""
        score = 0

        # Temporarily place stone
        board[x][y] = color

        # Check what threats it creates
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        max_length = 0

        for dx, dy in directions:
            length = self._count_line_length(board, x, y, dx, dy, color)
            max_length = max(max_length, length)

        # Score based on threat level
        if max_length >= 5:
            score += 50000
        elif max_length == 4:
            score += 5000
        elif max_length == 3:
            score += 500
        elif max_length == 2:
            score += 50

        board[x][y] = Defines.NOSTONE

        # Positional factors
        # Center bonus
        center_dist = abs(x - 10) + abs(y - 10)
        score += (20 - center_dist) * 3

        # Adjacent stones
        adjacent = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (1 <= nx <= 19 and 1 <= ny <= 19 and
                        board[nx][ny] == color):
                    adjacent += 1

        score += adjacent * 15

        return score

    def _count_line_length(self, board, x, y, dx, dy, color):
        """Count consecutive stones in direction."""
        count = 1

        # Forward
        tx, ty = x + dx, y + dy
        while (1 <= tx <= 19 and 1 <= ty <= 19 and board[tx][ty] == color):
            count += 1
            tx += dx
            ty += dy

        # Backward
        tx, ty = x - dx, y - dy
        while (1 <= tx <= 19 and 1 <= ty <= 19 and board[tx][ty] == color):
            count += 1
            tx -= dx
            ty -= dy

        return count

    def _create_center_move(self):
        """Fallback center move."""
        move = StoneMove()
        move.positions[0].x = 10
        move.positions[0].y = 10
        move.positions[1].x = 11
        move.positions[1].y = 11
        move.score = 0
        return move

    def update_history(self, move, depth, caused_cutoff):
        """Update move history for better ordering."""
        if caused_cutoff:
            move_key = (
                (move.positions[0].x, move.positions[0].y),
                (move.positions[1].x, move.positions[1].y)
            )

            if move_key not in self.move_history:
                self.move_history[move_key] = 0

            self.move_history[move_key] += depth * depth

    def clear_history(self):
        """Clear move history."""
        self.move_history.clear()
