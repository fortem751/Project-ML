"""
Professional Game Engine for Connect 6
Integrates all advanced components
"""

from defines import *
from tools import init_board, make_move, is_win_by_premove, msg2move, move2msg, print_board, log_to_file
import sys
from search_engine import SearchEngine
import time


def flush_output():
    try:
        sys.stdout.flush()
    except (BrokenPipeError, IOError):
        pass


class GameEngine:
    """Professional Connect 6 game engine."""

    def __init__(self, name=Defines.ENGINE_NAME):
        if name and len(name) > 0:
            if len(name) < Defines.MSG_LENGTH:
                self.m_engine_name = name

        self.m_alphabeta_depth = 6  # Deeper search by default
        self.m_time_limit = 8.0
        self.m_board = [
            [0] * Defines.GRID_NUM for i in range(Defines.GRID_NUM)]
        self.init_game()
        self.m_search_engine = SearchEngine()
        self.m_best_move = StoneMove()
        self.m_vcf = False
        self.m_chess_type = Defines.BLACK
        self.move_count = 0

    def init_game(self):
        init_board(self.m_board)
        self.move_count = 0

    def on_help(self):
        print(f"=== {self.m_engine_name} - Professional Connect 6 Engine ===")
        print("Commands:")
        print("  name          - Print engine name")
        print("  print         - Print current board")
        print("  exit/quit     - Exit engine")
        print("  black XXXX    - Place black stone(s)")
        print("  white XXXX    - Place white stone(s)")
        print("  next          - Calculate next move")
        print("  move XXXX     - Opponent move, then respond")
        print("  new black     - New game as black")
        print("  new white     - New game as white")
        print("  depth N       - Set time limit (N seconds)")
        print("  vcf/unvcf     - Ignored")
        print("  help          - This help")
        print("=" * 60)
        flush_output()

    def validate_and_fix_move(self, move):
        for pos in move.positions:
            if pos.x < 1:
                pos.x = 1
            elif pos.x > 19:
                pos.x = 19
            if pos.y < 1:
                pos.y = 1
            elif pos.y > 19:
                pos.y = 19
        return move

    def find_empty_near(self, x, y):
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = x + dx, y + dy
                if 1 <= nx <= 19 and 1 <= ny <= 19:
                    if self.m_board[nx][ny] == Defines.NOSTONE:
                        return (nx, ny)
        return (10, 10)

    def ensure_valid_empty_move(self, move):
        if (not (1 <= move.positions[0].x <= 19 and 1 <= move.positions[0].y <= 19) or
                self.m_board[move.positions[0].x][move.positions[0].y] != Defines.NOSTONE):
            move.positions[0].x, move.positions[0].y = self.find_empty_near(
                10, 10)

        if (not (1 <= move.positions[1].x <= 19 and 1 <= move.positions[1].y <= 19) or
                self.m_board[move.positions[1].x][move.positions[1].y] != Defines.NOSTONE):
            x, y = self.find_empty_near(
                move.positions[0].x, move.positions[0].y)
            if x == move.positions[0].x and y == move.positions[0].y:
                x, y = self.find_empty_near(x + 1, y + 1)
            move.positions[1].x, move.positions[1].y = x, y
        return move

    def run(self):
        """Main game loop."""
        print(f"\n{self.m_engine_name} - Professional Edition")
        print("Using: Opening Book, Zobrist Hashing, Pattern Recognition")
        print("Advanced: Null-Move, LMR, Aspiration Windows, PVS")
        print("=" * 60)
        self.on_help()

        while True:
            try:
                msg = input().strip()
                log_to_file(msg)

                if msg == "name":
                    print(f"name {self.m_engine_name}")
                    flush_output()

                elif msg == "exit" or msg == "quit":
                    print("Goodbye!")
                    break

                elif msg == "print":
                    print_board(self.m_board, self.m_best_move)
                    flush_output()

                elif msg.startswith("black"):
                    self.m_best_move = msg2move(msg[6:])
                    self.m_best_move = self.validate_and_fix_move(
                        self.m_best_move)
                    make_move(self.m_board, self.m_best_move, Defines.BLACK)
                    self.m_chess_type = Defines.BLACK
                    self.move_count += 1

                elif msg.startswith("white"):
                    self.m_best_move = msg2move(msg[6:])
                    self.m_best_move = self.validate_and_fix_move(
                        self.m_best_move)
                    make_move(self.m_board, self.m_best_move, Defines.WHITE)
                    self.m_chess_type = Defines.WHITE
                    self.move_count += 1

                elif msg == "next":
                    self.m_chess_type = self.m_chess_type ^ 3
                    if self.search_a_move(self.m_chess_type, self.m_best_move):
                        self.m_best_move = self.ensure_valid_empty_move(
                            self.m_best_move)
                        make_move(self.m_board, self.m_best_move,
                                  self.m_chess_type)
                        self.move_count += 1
                        print(f"move {move2msg(self.m_best_move)}")
                        flush_output()

                elif msg.startswith("new"):
                    self.init_game()
                    if len(msg) > 4 and msg[4:].strip() == "black":
                        self.m_best_move = msg2move("JJ")
                        make_move(self.m_board, self.m_best_move,
                                  Defines.BLACK)
                        self.m_chess_type = Defines.BLACK
                        self.move_count = 1
                        print("move JJ")
                        flush_output()
                    else:
                        self.m_chess_type = Defines.WHITE
                        self.move_count = 0

                elif msg.startswith("move"):
                    self.m_best_move = msg2move(msg[5:])
                    self.m_best_move = self.validate_and_fix_move(
                        self.m_best_move)
                    make_move(self.m_board, self.m_best_move,
                              self.m_chess_type ^ 3)
                    self.move_count += 1

                    if is_win_by_premove(self.m_board, self.m_best_move):
                        print("We lost!")
                        flush_output()
                    else:
                        if self.search_a_move(self.m_chess_type, self.m_best_move):
                            self.m_best_move = self.ensure_valid_empty_move(
                                self.m_best_move)
                            make_move(self.m_board, self.m_best_move,
                                      self.m_chess_type)
                            self.move_count += 1
                            print(f"move {move2msg(self.m_best_move)}")
                            flush_output()

                elif msg.startswith("depth"):
                    try:
                        parts = msg.split()
                        if len(parts) >= 2:
                            depth_value = int(parts[1])
                            self.m_time_limit = float(depth_value)

                            # Adjust search depth based on time
                            if depth_value <= 2:
                                self.m_alphabeta_depth = 4
                            elif depth_value <= 4:
                                self.m_alphabeta_depth = 6  # PATCHED: Increased from 5
                            elif depth_value <= 8:
                                self.m_alphabeta_depth = 6
                            else:
                                self.m_alphabeta_depth = 7

                            print(
                                f"Time limit: {self.m_time_limit}s, Depth: {self.m_alphabeta_depth}")
                            flush_output()
                    except (ValueError, IndexError):
                        print("Invalid depth command. Usage: depth <seconds>")
                        flush_output()

                elif msg == "vcf":
                    self.m_vcf = True

                elif msg == "unvcf":
                    self.m_vcf = False

                elif msg == "help":
                    self.on_help()

                else:
                    print(f"Unknown command: {msg}")
                    flush_output()

            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
                log_to_file(f"Error: {e}")
                import traceback
                traceback.print_exc()
                flush_output()

        return 0

    def search_a_move(self, our_color, best_move):
        """Execute search and return best move."""
        try:
            print(f"\n--- Move {self.move_count} Search ---")
            start = time.perf_counter()

            # Update move number in search engine
            self.m_search_engine.move_number = self.move_count

            # Initialize search
            self.m_search_engine.before_search(
                self.m_board, self.m_chess_type, self.m_alphabeta_depth
            )

            # Run iterative deepening search
            score = self.m_search_engine.iterative_deepening_search(
                self.m_alphabeta_depth, self.m_time_limit, our_color, best_move
            )

            end = time.perf_counter()

            # Validate result
            self.validate_and_fix_move(best_move)

            # Additional validation
            if (1 <= best_move.positions[0].x <= 19 and 1 <= best_move.positions[0].y <= 19):
                if self.m_board[best_move.positions[0].x][best_move.positions[0].y] != Defines.NOSTONE:
                    best_move.positions[0].x, best_move.positions[0].y = self.find_empty_near(
                        10, 10)

            if (1 <= best_move.positions[1].x <= 19 and 1 <= best_move.positions[1].y <= 19):
                if self.m_board[best_move.positions[1].x][best_move.positions[1].y] != Defines.NOSTONE:
                    x, y = self.find_empty_near(
                        best_move.positions[0].x, best_move.positions[0].y)
                    if x == best_move.positions[0].x and y == best_move.positions[0].y:
                        x, y = self.find_empty_near(x + 1, y + 1)
                    best_move.positions[1].x, best_move.positions[1].y = x, y

            # Print summary
            elapsed = end - start
            nps = self.m_search_engine.m_total_nodes / max(elapsed, 0.001)

            print(f"Search complete: {elapsed:.2f}s")
            print(
                f"Nodes: {self.m_search_engine.m_total_nodes:,} ({nps:.0f} nps)")
            print(f"Score: {score}")
            print(f"Move: {move2msg(best_move)}")
            print("-" * 60)

            flush_output()
            return True

        except Exception as e:
            print(f"Search error: {e}")
            log_to_file(f"Search error: {e}")
            import traceback
            traceback.print_exc()

            # Fallback to center
            best_move.positions[0].x, best_move.positions[0].y = self.find_empty_near(
                10, 10)
            best_move.positions[1].x, best_move.positions[1].y = self.find_empty_near(
                10, 11)
            flush_output()
            return True


if __name__ == "__main__":
    game_engine = GameEngine()
    game_engine.run()
