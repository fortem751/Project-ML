"""
Professional Search Engine for Connect 6
Includes: Alpha-Beta, Null-Move, LMR, Aspiration Windows, PVS
"""

from defines import *
from tools import make_move, unmake_move, is_win_by_premove
from evaluation import Evaluator
from move_generator import MoveGenerator
from zobrist_hash import TranspositionTable
from opening_book import OpeningBook
import time


class SearchEngine:
    """Professional game tree search engine."""

    def __init__(self):
        self.m_board = None
        self.m_chess_type = None
        self.m_alphabeta_depth = None
        self.m_total_nodes = 0

        # Core components
        self.evaluator = Evaluator()
        self.move_generator = MoveGenerator()
        self.transposition_table = TranspositionTable(max_size=500000)
        self.opening_book = OpeningBook()

        # Search parameters
        self.max_time = None
        self.start_time = None
        self.time_check_counter = 0

        # Move ordering
        self.killer_moves = [[None, None] for _ in range(30)]
        self.pv_table = {}

        # Statistics
        self.nodes_per_depth = [0] * 30
        self.cutoffs_first_move = 0
        self.cutoffs_other_moves = 0

        # Search configuration
        self.use_null_move = True
        self.use_lmr = True  # Late Move Reductions
        self.use_aspiration = True
        self.null_move_reduction = 2
        self.lmr_threshold = 4  # Start reducing after 4th move

        self.move_number = 0  # Track move number for opening book

    def before_search(self, board, color, alphabeta_depth):
        """Initialize search."""
        self.m_board = [row[:] for row in board]
        self.m_chess_type = color
        self.m_alphabeta_depth = alphabeta_depth
        self.m_total_nodes = 0

        # Soft clear transposition table (keep recent entries)
        self.transposition_table.soft_clear()

        self.max_time = alphabeta_depth * 2.5
        self.start_time = time.perf_counter()
        self.time_check_counter = 0

        # Reset killers for new search
        self.killer_moves = [[None, None] for _ in range(30)]
        self.pv_table.clear()

        # Reset statistics
        self.nodes_per_depth = [0] * 30
        self.cutoffs_first_move = 0
        self.cutoffs_other_moves = 0

    def iterative_deepening_search(self, max_depth, time_limit, our_color, best_move):
        """
        Iterative deepening with aspiration windows.
        Professional implementation with all optimizations.
        """
        self.max_time = time_limit
        self.start_time = time.perf_counter()

        # CRITICAL: Check tactics FIRST (before opening book!)
        immediate_wins = self.evaluator.detect_immediate_win(
            self.m_board, our_color)
        if immediate_wins:
            print(f"IMMEDIATE WIN FOUND!")
            best_move.positions[0].x, best_move.positions[0].y = immediate_wins[0]
            x2, y2 = self._find_second_stone(immediate_wins[0], self.m_board)
            best_move.positions[1].x, best_move.positions[1].y = x2, y2
            return Defines.MAXINT - 1

        opponent = Defines.BLACK if our_color == Defines.WHITE else Defines.WHITE
        opponent_wins = self.evaluator.detect_immediate_win(
            self.m_board, opponent)

        if opponent_wins:
            print(f"BLOCKING {len(opponent_wins)} OPPONENT THREAT(S)")
            if len(opponent_wins) >= 2:
                # Multiple threats - block both
                best_move.positions[0].x, best_move.positions[0].y = opponent_wins[0]
                best_move.positions[1].x, best_move.positions[1].y = opponent_wins[1]
                return Defines.MININT + 1

        # NOW check opening book (only if no immediate tactics)
        book_pos1, book_pos2, in_book = self.opening_book.get_book_move(
            self.m_board, our_color, self.move_number
        )

        if in_book:
            print(f"Using opening book move")
            best_move.positions[0].x, best_move.positions[0].y = book_pos1
            if book_pos2:
                best_move.positions[1].x, best_move.positions[1].y = book_pos2
            else:
                # Single stone (black's first move)
                best_move.positions[1].x, best_move.positions[1].y = book_pos1
            return 0

        # Iterative deepening loop
        best_score = 0
        best_move.positions[0].x = 10
        best_move.positions[0].y = 10
        best_move.positions[1].x = 10
        best_move.positions[1].y = 10

        for depth in range(1, max_depth + 1):
            # Time check
            if (time.perf_counter() - self.start_time) > time_limit * 0.85:
                print(f"Time limit approaching, stopping at depth {depth-1}")
                break

            temp_move = StoneMove()

            # Use aspiration windows for depth >= 3
            if depth >= 3 and self.use_aspiration and abs(best_score) < 50000:
                window = 200 + depth * 50
                alpha = best_score - window
                beta = best_score + window

                score = self._alpha_beta_root(
                    depth, alpha, beta, our_color, temp_move)

                # Re-search if we fall outside window
                if score <= alpha or score >= beta:
                    print(f"  Aspiration window failed, re-searching...")
                    score = self._alpha_beta_root(
                        depth, Defines.MININT, Defines.MAXINT, our_color, temp_move
                    )
            else:
                score = self._alpha_beta_root(
                    depth, Defines.MININT, Defines.MAXINT, our_color, temp_move
                )

            # Update best move if we completed depth
            if (time.perf_counter() - self.start_time) < time_limit * 0.95:
                self._validate_move(temp_move)
                best_move.positions[0].x = temp_move.positions[0].x
                best_move.positions[0].y = temp_move.positions[0].y
                best_move.positions[1].x = temp_move.positions[1].x
                best_move.positions[1].y = temp_move.positions[1].y
                best_score = score

                # Print search info
                elapsed = time.perf_counter() - self.start_time
                nodes_per_sec = self.m_total_nodes / max(elapsed, 0.001)

                print(f"Depth {depth}: score={score}, "
                      f"nodes={self.m_total_nodes}, "
                      f"nps={nodes_per_sec:.0f}, "
                      f"time={elapsed:.2f}s")

                # Stop if we found a forced win/loss
                if abs(score) > 5000000:
                    print(f"Forced sequence detected, stopping search")
                    break
            else:
                print(
                    f"Depth {depth} incomplete, using depth {depth-1} result")
                break

        self._validate_move(best_move)

        # Print transposition table stats
        tt_stats = self.transposition_table.get_stats()
        print(
            f"TT: {tt_stats['size']} entries, {tt_stats['hit_rate']:.1f}% hit rate")

        return best_score

    def _alpha_beta_root(self, depth, alpha, beta, color, best_move):
        """Root search with PV handling."""
        self.m_total_nodes += 1
        self.nodes_per_depth[depth] += 1

        # Generate moves
        pv_move = self.pv_table.get(self._hash_board(), None)
        moves = self.move_generator.generate_moves(
            self.m_board, color, depth, max_moves=35, pv_move=pv_move
        )

        if not moves:
            return self.evaluator.evaluate_position(self.m_board, color)

        best_score = Defines.MININT
        best_local_move = None

        # Try PV move first if available
        if pv_move and pv_move in moves:
            moves.remove(pv_move)
            moves.insert(0, pv_move)

        for i, move in enumerate(moves):
            self._validate_move(move)
            make_move(self.m_board, move, color)

            # PVS (Principal Variation Search)
            if i == 0:
                # Full window search for first move
                score = -self._alpha_beta(
                    depth - 1, -beta, -alpha, color ^ 3, StoneMove(), move
                )
            else:
                # Null window search for other moves
                score = -self._alpha_beta(
                    depth - 1, -alpha - 1, -alpha, color ^ 3, StoneMove(), move
                )

                # Re-search if it's better than expected
                if alpha < score < beta:
                    score = -self._alpha_beta(
                        depth - 1, -beta, -score, color ^ 3, StoneMove(), move
                    )

            unmake_move(self.m_board, move)

            if score > best_score:
                best_score = score
                best_local_move = move

                if score > alpha:
                    alpha = score
                    # Update PV
                    self.pv_table[self._hash_board()] = move

        if best_local_move:
            best_move.positions[0].x = best_local_move.positions[0].x
            best_move.positions[0].y = best_local_move.positions[0].y
            best_move.positions[1].x = best_local_move.positions[1].x
            best_move.positions[1].y = best_local_move.positions[1].y

        return best_score

    def _alpha_beta(self, depth, alpha, beta, color, best_move, pre_move):
        """
        Main alpha-beta search with all optimizations:
        - Transposition table
        - Null-move pruning
        - Late move reductions
        - Killer move ordering
        - Tactical extensions
        """
        # Periodic time check (every 100 nodes)
        self.time_check_counter += 1
        if self.time_check_counter % 100 == 0:
            if self.max_time and (time.perf_counter() - self.start_time) > self.max_time:
                return self.evaluator.evaluate_position(self.m_board, self.m_chess_type)

        # Check for game end
        if is_win_by_premove(self.m_board, pre_move):
            if color == self.m_chess_type:
                return Defines.MININT + depth
            else:
                return Defines.MAXINT - depth

        # Transposition table probe
        board_hash = self._hash_board()
        tt_hit, tt_score, tt_move = self.transposition_table.probe(
            board_hash, depth, alpha, beta
        )

        if tt_hit:
            return tt_score

        # Leaf node - evaluate or extend
        if depth <= 0:
            # Check if position is tactical (needs extension)
            threat_info = self.evaluator.get_threat_analysis(
                self.m_board, color)

            if threat_info['critical_situation'] and depth > -4:
                # Extend search in critical positions
                return self._quiescence_search(alpha, beta, color, 3)
            else:
                return self._quiescence_search(alpha, beta, color, 2)

        self.m_total_nodes += 1
        self.nodes_per_depth[depth] += 1

        # Get threat info for null-move pruning decision
        threat_info = self.evaluator.get_threat_analysis(self.m_board, color)

        # Null-move pruning (don't use in endgame or when in check)
        if (self.use_null_move and depth >= 3 and not threat_info['critical_situation']):
            # Try skipping our move
            null_score = -self._alpha_beta(
                depth - 1 - self.null_move_reduction, -beta, -beta + 1,
                color ^ 3, StoneMove(), StoneMove()
            )

            if null_score >= beta:
                # Null move caused cutoff
                return beta

        # Generate moves
        pv_move = tt_move if tt_move else self.pv_table.get(board_hash)
        moves = self.move_generator.generate_moves(
            self.m_board, color, depth, max_moves=35, pv_move=pv_move
        )

        if not moves:
            return self.evaluator.evaluate_position(self.m_board, self.m_chess_type)

        # Order moves (PV first, then killers, then others)
        moves = self._order_moves(moves, depth, pv_move)

        best_score = Defines.MININT if color == self.m_chess_type else Defines.MAXINT
        best_local_move = None
        moves_searched = 0
        flag = TranspositionTable.UPPER_BOUND if color == self.m_chess_type else TranspositionTable.LOWER_BOUND

        for move in moves:
            self._validate_move(move)
            make_move(self.m_board, move, color)

            # Late Move Reductions (LMR)
            if (self.use_lmr and moves_searched >= self.lmr_threshold and
                    depth >= 3 and not threat_info['critical_situation']):
                # Reduce depth for later moves
                reduction = 1 if moves_searched < 8 else 2
                score = -self._alpha_beta(
                    depth - 1 - reduction, -beta, -alpha,
                    color ^ 3, StoneMove(), move
                )

                # Re-search at full depth if it looks good
                if score > alpha:
                    score = -self._alpha_beta(
                        depth - 1, -beta, -alpha, color ^ 3, StoneMove(), move
                    )
            else:
                # Normal search
                score = -self._alpha_beta(
                    depth - 1, -beta, -alpha, color ^ 3, StoneMove(), move
                )

            unmake_move(self.m_board, move)
            moves_searched += 1

            # Update best
            if color == self.m_chess_type:
                if score > best_score:
                    best_score = score
                    best_local_move = move

                    if score > alpha:
                        alpha = score
                        flag = TranspositionTable.EXACT

                        if score >= beta:
                            # Beta cutoff
                            flag = TranspositionTable.LOWER_BOUND
                            self._update_killers(move, depth)
                            self.move_generator.update_history(
                                move, depth, True)

                            if moves_searched == 1:
                                self.cutoffs_first_move += 1
                            else:
                                self.cutoffs_other_moves += 1

                            break
            else:
                if score < best_score:
                    best_score = score
                    best_local_move = move

                    if score < beta:
                        beta = score
                        flag = TranspositionTable.EXACT

                        if score <= alpha:
                            # Alpha cutoff
                            flag = TranspositionTable.UPPER_BOUND
                            self._update_killers(move, depth)
                            self.move_generator.update_history(
                                move, depth, True)
                            break

        # Store in transposition table
        self.transposition_table.store(
            board_hash, depth, best_score, flag, best_local_move
        )

        return best_score

    def _quiescence_search(self, alpha, beta, color, depth):
        """Quiescence search for tactical positions."""
        if depth <= 0:
            return self.evaluator.evaluate_position(self.m_board, self.m_chess_type)

        # Stand pat
        stand_pat = self.evaluator.evaluate_position(
            self.m_board, self.m_chess_type)

        if color == self.m_chess_type:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        # Generate only tactical moves
        tactical_moves = self._generate_tactical_moves(color)

        for move in tactical_moves[:8]:
            make_move(self.m_board, move, color)
            score = self._quiescence_search(alpha, beta, color ^ 3, depth - 1)
            unmake_move(self.m_board, move)

            if color == self.m_chess_type:
                alpha = max(alpha, score)
                if alpha >= beta:
                    return beta
            else:
                beta = min(beta, score)
                if beta <= alpha:
                    return alpha

        return alpha if color == self.m_chess_type else beta

    def _generate_tactical_moves(self, color):
        """Generate captures and threats for quiescence."""
        moves = []

        # Get critical moves (threats)
        critical = self.evaluator.detect_critical_moves(self.m_board, color)

        for move_info in critical[:10]:
            if move_info['threat_level'] >= 3:
                # Try combining with other threats
                for move_info2 in critical[:10]:
                    if move_info['position'] != move_info2['position']:
                        move = StoneMove()
                        move.positions[0].x, move.positions[0].y = move_info['position']
                        move.positions[1].x, move.positions[1].y = move_info2['position']
                        moves.append(move)

                        if len(moves) >= 8:
                            return moves

        return moves

    def _order_moves(self, moves, depth, pv_move):
        """Order moves for better pruning."""
        if not moves:
            return moves

        # PV move first
        if pv_move and pv_move in moves:
            moves.remove(pv_move)
            moves.insert(0, pv_move)

        # Killer moves next
        if depth < len(self.killer_moves):
            for killer in self.killer_moves[depth]:
                if killer and killer in moves:
                    moves.remove(killer)
                    moves.insert(1 if pv_move else 0, killer)

        # Rest sorted by move score
        start_idx = 1 if pv_move else 0
        remaining = moves[start_idx:]
        remaining.sort(key=lambda m: m.score if hasattr(
            m, 'score') else 0, reverse=True)
        moves[start_idx:] = remaining

        return moves

    def _update_killers(self, move, depth):
        """Update killer move heuristic."""
        if depth < len(self.killer_moves):
            if not self._moves_equal(move, self.killer_moves[depth][0]):
                self.killer_moves[depth][1] = self.killer_moves[depth][0]
                self.killer_moves[depth][0] = self._copy_move(move)

    def _moves_equal(self, move1, move2):
        """Check if two moves are equal."""
        if move1 is None or move2 is None:
            return False
        return (move1.positions[0].x == move2.positions[0].x and
                move1.positions[0].y == move2.positions[0].y and
                move1.positions[1].x == move2.positions[1].x and
                move1.positions[1].y == move2.positions[1].y)

    def _copy_move(self, move):
        """Create a copy of a move."""
        new_move = StoneMove()
        new_move.positions[0].x = move.positions[0].x
        new_move.positions[0].y = move.positions[0].y
        new_move.positions[1].x = move.positions[1].x
        new_move.positions[1].y = move.positions[1].y
        new_move.score = move.score if hasattr(move, 'score') else 0
        return new_move

    def _validate_move(self, move):
        """Ensure move has valid coordinates."""
        for pos in move.positions:
            pos.x = max(1, min(19, pos.x))
            pos.y = max(1, min(19, pos.y))

    def _hash_board(self):
        """Simple board hash for now."""
        return hash(tuple(tuple(row) for row in self.m_board))

    def _find_second_stone(self, pos1, board):
        """Find good position for second stone."""
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x2, y2 = pos1[0] + dx, pos1[1] + dy
                if (1 <= x2 <= 19 and 1 <= y2 <= 19 and
                        board[x2][y2] == Defines.NOSTONE and (x2, y2) != pos1):
                    return x2, y2
        return 10, 10
