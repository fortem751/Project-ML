

from defines import *
from tools import init_board, make_move, unmake_move, is_win_by_premove, msg2move, move2msg, print_board
import sys
import os
from search_engine import SearchEngine
import time
import random


def debug_log(msg):
    try:
        with open("/tmp/connect6_debug.txt", "a") as f:
            f.write(f"{time.time()}: {msg}\n")
            f.flush()
    except:
        pass


debug_log("=== ENGINE STARTED ===")

os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1, closefd=False)


class GameEngine:
    def __init__(self, name=Defines.ENGINE_NAME):
        debug_log("Init")
        self.m_engine_name = Defines.ENGINE_NAME
        if name and 0 < len(name) < Defines.MSG_LENGTH:
            self.m_engine_name = name

        self.m_alphabeta_depth = 6  # Fast for testing - increase to 4 for better play
        self.m_time_limit = 10.0

        self.m_board = [
            [0] * Defines.GRID_NUM for _ in range(Defines.GRID_NUM)]
        self.m_best_move = StoneMove()
        self.m_vcf = False
        self.m_chess_type = Defines.BLACK
        self.move_count = 0
        self.m_search_engine = SearchEngine()
        self.init_game()

    def init_game(self):
        init_board(self.m_board)
        self.m_chess_type = Defines.BLACK
        self.move_count = 0
        self.m_best_move = StoneMove()
        self.m_search_engine.init_game(self.m_board, self.m_chess_type)

    def set_color(self, color):
        self.m_chess_type = color
        self.m_search_engine.m_chess_type = color

    def _find_random_empty_pair(self, board):
        empty_positions = []
        for i in range(1, Defines.GRID_NUM - 1):
            for j in range(1, Defines.GRID_NUM - 1):
                if board[i][j] == Defines.NOSTONE:
                    empty_positions.append(Position(i, j))

        if len(empty_positions) < 2:
            move = StoneMove()
            move.positions[0] = Position(10, 10)
            move.positions[1] = Position(11, 10)
            return move

        pos1 = random.choice(empty_positions)
        empty_positions.remove(pos1)

        adjacent = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = pos1.x + dx, pos1.y + dy
                if 1 <= nx <= 19 and 1 <= ny <= 19 and board[nx][ny] == Defines.NOSTONE:
                    adjacent.append(Position(nx, ny))

        pos2 = random.choice(
            adjacent) if adjacent else random.choice(empty_positions)

        move = StoneMove()
        move.positions[0] = pos1
        move.positions[1] = pos2
        return move

    def _find_single_stone_move(self):
        pos = Position(10, 10)
        move = StoneMove()
        move.positions[0] = pos
        move.positions[1] = pos
        debug_log(
            f"Created single stone move at J10: {move.positions[0].x},{move.positions[0].y}")
        return move

    def search_a_move(self):
        debug_log(
            f"search_a_move called (depth={self.m_alphabeta_depth}, time={self.m_time_limit})")
        start_time = time.time()

        try:
            player_color = self.m_chess_type
            is_first = (self.move_count == 0) and (
                player_color == Defines.BLACK)

            if is_first:
                debug_log("First move - returning J10")
                best_move = self._find_single_stone_move()
            else:
                debug_log("Starting search...")

                try:
                    score, best_move = self.m_search_engine.iterative_deepening_search(
                        self.m_board, player_color, self.m_alphabeta_depth, self.m_time_limit)

                    elapsed = time.time() - start_time
                    debug_log(
                        f"Search completed in {elapsed:.2f}s, score={score}")

                except Exception as search_error:
                    debug_log(f"Search failed: {search_error}")
                    import traceback
                    debug_log(traceback.format_exc())
                    debug_log("Using random move instead")
                    best_move = self._find_random_empty_pair(self.m_board)

                if best_move is None:
                    debug_log("ERROR: Search returned None, using random")
                    best_move = self._find_random_empty_pair(self.m_board)
                else:
                    pos1_occupied = self.m_board[best_move.positions[0]
                                                 .x][best_move.positions[0].y] != Defines.NOSTONE
                    pos2_occupied = self.m_board[best_move.positions[1]
                                                 .x][best_move.positions[1].y] != Defines.NOSTONE

                    if pos1_occupied or pos2_occupied:
                        debug_log(
                            "ERROR: Search returned occupied position, using random")
                        best_move = self._find_random_empty_pair(self.m_board)

            self.m_best_move = best_move
            make_move(self.m_board, best_move, player_color)
            self.move_count += 1

            move_msg = move2msg(best_move)
            total_time = time.time() - start_time
            debug_log(
                f"Move generated: {move_msg} (total time: {total_time:.2f}s)")
            return move_msg

        except Exception as e:
            debug_log(f"FATAL ERROR in search_a_move: {e}")
            import traceback
            debug_log(traceback.format_exc())
            return "J10J10"

    def parse_command(self, cmd_line):
        if cmd_line is None:
            return

        cmd_line = cmd_line.strip()
        debug_log(f">>> CMD: '{cmd_line}'")

        if not cmd_line:
            return

        try:
            parts = cmd_line.lower().split()
            cmd = parts[0]

            if cmd == "name":
                # CRITICAL: GUI expects "name TIA.Connect6"
                response = "name " + self.m_engine_name
                print(response, flush=True)
                debug_log(f"<<< {response}")

            elif cmd == "next":
                debug_log("Processing 'next' command - generating move")
                move_msg = self.search_a_move()
                # CRITICAL: GUI expects "move J10J10" not just "J10J10"
                response = "move " + move_msg
                print(response, flush=True)
                debug_log(f"<<< {response}")

            elif cmd == "black" and len(parts) >= 2:
                move = msg2move(parts[1])
                if move:
                    make_move(self.m_board, move, Defines.BLACK)
                    self.move_count += 1
                    debug_log(f"Black played: {parts[1]}")

            elif cmd == "white" and len(parts) >= 2:
                move = msg2move(parts[1])
                if move:
                    make_move(self.m_board, move, Defines.WHITE)
                    self.move_count += 1
                    debug_log(f"White played: {parts[1]}")

            elif cmd == "new":
                self.init_game()
                if len(parts) > 1:
                    if parts[1] == "black":
                        self.set_color(Defines.BLACK)
                        debug_log("New game as BLACK")
                    elif parts[1] == "white":
                        self.set_color(Defines.WHITE)
                        debug_log("New game as WHITE")
                    else:
                        debug_log(f"New game with args: {parts[1:]}")

            elif cmd == "depth" and len(parts) >= 2:
                try:
                    self.m_alphabeta_depth = 6  # Force depth 6
                    debug_log(f"Depth set to {self.m_alphabeta_depth}")
                except:
                    pass

            elif cmd == "vcf":
                self.m_vcf = True
                debug_log("VCF enabled")

            elif cmd == "unvcf":
                self.m_vcf = False
                debug_log("VCF disabled")

            elif cmd in ("exit", "quit"):
                sys.exit(0)

        except Exception as e:
            debug_log(f"ERROR in parse_command: {e}")
            import traceback
            debug_log(traceback.format_exc())

    def main_loop(self):
        debug_log("=== MAIN LOOP STARTED ===")
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                self.parse_command(line)
            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                debug_log(f"ERROR in main_loop: {e}")


if __name__ == "__main__":
    debug_log("ENGINE STARTING")
    GameEngine().main_loop()
    debug_log("ENGINE STOPPED")
