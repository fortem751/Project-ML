
from defines import *
from tools import make_move, unmake_move, is_win_by_premove
from evaluation import Evaluator
from move_generator import MoveGenerator
from zobrist_hash import TranspositionTable
from opening_book import OpeningBook
import time


class SearchEngine:

    def __init__(self):
        # Board state
        self.m_board = [[0 for _ in range(Defines.GRID_NUM)]
                        for _ in range(Defines.GRID_NUM)]
        self.m_chess_type = Defines.BLACK

        # Core components
        self.evaluator = Evaluator()
        self.move_generator = MoveGenerator()
        self.transposition_table = TranspositionTable()
        self.opening_book = OpeningBook()

        # Search settings
        self.m_ab_cut = 0
        self.m_total_nodes = 0
        self.m_max_depth = 0
        self.m_search_aborted = False
        self.max_time = 0
        self.start_time = 0
        self.nodes_per_depth = [0] * 64

        # Move ordering / history
        self.history_moves = {}
        self.killer_moves = [[None, None] for _ in range(64)]

        # Initialize components' caches
        self.evaluator.clear_cache()
        self.transposition_table.clear()
        self.opening_book.load_book()

    def init_game(self, board, color):

        self.m_board = board
        self.m_chess_type = color

        self.m_total_nodes = 0
        self.m_search_aborted = False

        self.transposition_table.clear()
        self.evaluator.clear_cache()
        self.history_moves = {}
        self.killer_moves = [[None, None] for _ in range(64)]

    def iterative_deepening_search(self, board, color, max_depth, time_limit):

        self.m_board = board
        self.m_chess_type = color
        self.m_max_depth = max_depth
        self.max_time = time_limit
        self.start_time = time.time()
        self.m_search_aborted = False
        self_best_score = 0

        self_best_move = self._create_center_move()

        book_move, book_score = self._check_opening_book()
        if book_move:
            return book_score, book_move

        alpha = Defines.MININT
        beta = Defines.MAXINT

        for depth in range(1, max_depth + 1):
            if self._check_time():
                break

            score, best_move = self.search_pvs(
                depth, alpha, beta, self.m_chess_type)

            if self.m_search_aborted:
                break

            if score <= alpha or score >= beta:
                score, best_move = self.search_pvs(
                    depth, Defines.MININT, Defines.MAXINT, self.m_chess_type)

            self_best_score = score

            if best_move.positions[0].x != 0:
                self_best_move = best_move

            alpha = self_best_score - 50
            beta = self_best_score + 50

        try:
            with open("/tmp/connect6_debug.txt", "a") as f:
                f.write(
                    f"{time.time()}: ID_SEARCH: score={self_best_score}, move=({self_best_move.positions[0].x},{self_best_move.positions[0].y})-({self_best_move.positions[1].x},{self_best_move.positions[1].y})\n")
                f.flush()
        except:
            pass
        return self_best_score, self_best_move

    def search_pvs(self, depth, alpha, beta, color):
        if self._check_time() and depth > 2:
            self.m_search_aborted = True
            score = self.evaluator.evaluate(self.m_board, color)
            return score, StoneMove()

        # BASE CASE: Return static score and a move object (Move object is ignored by caller)
        if depth <= 0:
            self.m_total_nodes += 1
            score = self.evaluator.evaluate(self.m_board, color)
            return score, StoneMove()

        # Check transposition table
        tt_entry = self.transposition_table.lookup(
            self._hash_board(color), depth, alpha, beta)
        if tt_entry:
            self.m_total_nodes += 1
            return tt_entry['score'], tt_entry['move']

        # Generate and order moves
        moves = self.move_generator.generate_moves(
            self.m_board, color, max_moves=80, pv_move=self._get_pv_move())

        legal_moves = []
        for move in moves:
            pos1 = move.positions[0]
            pos2 = move.positions[1]
            # Check if both target squares are empty (Defines.NOSTONE == 0)
            if self.m_board[pos1.x][pos1.y] == Defines.NOSTONE and \
               self.m_board[pos2.x][pos2.y] == Defines.NOSTONE:
                legal_moves.append(move)

        moves = legal_moves

        # If no moves (e.g., filtered all moves, board is full, or generator error)
        if not moves:
            # If no legal moves, return the evaluation and a safe move object
            return self.evaluator.evaluate(self.m_board, color), self._create_center_move()

        best_score = Defines.MININT
        # Initialize best_move to the best generated legal move
        best_move = moves[0]

        opponent_color = Defines.BLACK if color == Defines.WHITE else Defines.WHITE

        # PVS loop
        for i, move in enumerate(moves):

            make_move(self.m_board, move, color)

            if is_win_by_premove(self.m_board, move):
                score = Defines.MAXINT - (self.m_max_depth - depth)
            else:
                if i == 0:
                    score, _ = self.search_pvs(
                        depth - 1, -beta, -alpha, opponent_color)
                else:
                    score, _ = self.search_pvs(
                        depth - 1, -alpha - 1, -alpha, opponent_color)

                    if alpha < -score < beta:
                        score, _ = self.search_pvs(
                            depth - 1, -beta, -alpha, opponent_color)

                score = -score

            unmake_move(self.m_board, move)

            if score > best_score:
                best_score = score
                best_move = move

            if best_score > alpha:
                alpha = best_score

            if alpha >= beta:
                self.m_ab_cut += 1
                self.transposition_table.store(self._hash_board(
                    color), depth, best_score, best_move, 'BETA')

                self._update_history(move, depth, True)
                self._update_killer(move, depth)

                return best_score, best_move

        if best_move.positions[0].x != 0:
            tt_type = 'EXACT' if best_score > Defines.MININT else 'ALPHA'
            self.transposition_table.store(self._hash_board(
                color), depth, best_score, best_move, tt_type)

        return best_score, best_move

    def _check_opening_book(self):

        if self.m_board[10][10] == 0:
            book_move, book_score = self.opening_book.get_move('start_black')
            if book_move:
                return book_move, book_score

        current_hash = self.opening_book._hash_position(self.m_board)

        book_move, book_score = self.opening_book.get_move(current_hash)
        if book_move:
            return book_move, book_score

        return None, 0

    def _check_time(self):
        if time.time() - self.start_time > self.max_time:
            return True
        return False

    def _get_pv_move(self):
        tt_entry = self.transposition_table.lookup(
            self._hash_board(), 0, Defines.MININT, Defines.MAXINT)
        if tt_entry and tt_entry['move'].positions[0].x != 0:
            return tt_entry['move']
        return None

    def _update_history(self, move, depth, caused_cutoff):
        pass

    def _update_killer(self, move, depth):
        if depth > 1 and move not in self.killer_moves[depth]:
            self.killer_moves[depth][1] = self.killer_moves[depth][0]
            self.killer_moves[depth][0] = move

    def _validate_move(self, move):
        if (move.positions[0].x == move.positions[1].x and
                move.positions[0].y == move.positions[1].y):
            move.positions[1].x = move.positions[0].x + 1
            move.positions[1].y = move.positions[0].y

        for i in range(2):
            move.positions[i].x = max(1, min(19, move.positions[i].x))
            move.positions[i].y = max(1, min(19, move.positions[i].y))

    def _in_check(self, color):
        opponent = Defines.BLACK if color == Defines.WHITE else Defines.WHITE
        opponent_wins = self.evaluator.detect_immediate_win(
            self.m_board, opponent)
        return bool(opponent_wins)

    def _hash_board(self, color=None):
        if color is None:
            color = self.m_chess_type
        return self.transposition_table.zobrist.compute_hash(self.m_board, color)

    def _find_second_stone(self, pos1, board):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = pos1.x + dx, pos1.y + dy
                if board[nx][ny] == Defines.NOSTONE:
                    move = StoneMove()
                    move.positions[0] = pos1
                    move.positions[1].x = nx
                    move.positions[1].y = ny
                    return move
        return self._create_center_move()

    def _create_center_move(self):
        move = StoneMove()
        move.positions[0].x = 10
        move.positions[0].y = 10
        move.positions[1].x = 11
        move.positions[1].y = 11
        return move
