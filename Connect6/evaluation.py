
from defines import *
from tools import isValidPos
import time


class Evaluator:

    def __init__(self):
        self.weights = None
        self.cache = {}
        self.eval_count = 0

    def clear_cache(self):
        self.cache = {}

    def detect_immediate_win(self, board, color):
        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] != Defines.NOSTONE:
                    continue
                board[x][y] = color
                # Simple win check - would need check_win_at_position
                board[x][y] = Defines.NOSTONE
        return False

    def evaluate(self, board, color):
        self.eval_count += 1

        my_score = self._evaluate_color(board, color)
        opp_color = Defines.WHITE if color == Defines.BLACK else Defines.BLACK
        opp_score = self._evaluate_color(board, opp_color)

        final_score = my_score - opp_score

        # Log every 100 evaluations
        if self.eval_count % 100 == 0:
            try:
                with open("/tmp/connect6_debug.txt", "a") as f:
                    f.write(
                        f"{time.time()}: EVAL {self.eval_count}: color={color}, my={my_score}, opp={opp_score}, final={final_score}\n")
                    f.flush()
            except:
                pass

        return final_score

    def _evaluate_color(self, board, color):
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] != color:
                    continue

                for dx, dy in directions:
                    count = 1
                    empty_before = 0
                    empty_after = 0

                    nx, ny = x + dx, y + dy
                    while isValidPos(nx, ny):
                        if board[nx][ny] == color:
                            count += 1
                            nx += dx
                            ny += dy
                        elif board[nx][ny] == Defines.NOSTONE:
                            empty_after = 1
                            break
                        else:
                            break

                    nx, ny = x - dx, y - dy
                    while isValidPos(nx, ny):
                        if board[nx][ny] == color:
                            count += 1
                            nx -= dx
                            ny -= dy
                        elif board[nx][ny] == Defines.NOSTONE:
                            empty_before = 1
                            break
                        else:
                            break

                    if count >= 6:
                        score += 100000
                    elif count == 5:
                        if empty_before and empty_after:
                            score += 10000
                        else:
                            score += 5000
                    elif count == 4:
                        if empty_before and empty_after:
                            score += 1000
                        else:
                            score += 300
                    elif count == 3:
                        if empty_before and empty_after:
                            score += 100
                        else:
                            score += 30
                    elif count == 2:
                        if empty_before and empty_after:
                            score += 10
                        else:
                            score += 3

        return score
