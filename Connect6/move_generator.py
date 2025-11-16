

from defines import *
from tools import isValidPos
import random
import time

# UNIQUE SIGNATURE - Log on import
try:
    with open("/tmp/connect6_debug.txt", "a") as f:
        f.write(f"{time.time()}:  MOVE_GENERATOR Loaded \n")
        f.flush()
except:
    pass


class MoveGenerator:

    def __init__(self):
        # Log on creation too
        try:
            with open("/tmp/connect6_debug.txt", "a") as f:
                f.write(f"{time.time()}: MoveGenerator.__init__ called (v2.0)\n")
                f.flush()
        except:
            pass

    def generate_moves(self, board, color, max_moves=80, pv_move=None):
        """Generate moves: blocks first, attacks second, tactical third."""
        # Log on first call
        try:
            with open("/tmp/connect6_debug.txt", "a") as f:
                f.write(f"{time.time()}: generate_moves called (SMART v2.0)\n")
                f.flush()
        except:
            pass

        moves = []

        if pv_move:
            moves.append(pv_move)

        opp_color = Defines.WHITE if color == Defines.BLACK else Defines.BLACK

        # PRIORITY 1: Blocking moves
        blocking_moves = self._find_threat_blocking_moves(board, opp_color)
        moves.extend(blocking_moves[:20])

        # PRIORITY 2: Attacking moves
        attacking_moves = self._find_attacking_moves(board, color)
        moves.extend(attacking_moves[:20])

        # PRIORITY 3: Tactical moves
        tactical_moves = self._find_tactical_moves(board)
        moves.extend(tactical_moves[:40])

        # Remove duplicates
        seen = set()
        unique_moves = []
        for move in moves:
            key = (move.positions[0].x, move.positions[0].y,
                   move.positions[1].x, move.positions[1].y)
            if key not in seen:
                seen.add(key)
                unique_moves.append(move)

        return unique_moves[:max_moves] if unique_moves else [self._get_default_move()]

    def _find_threat_blocking_moves(self, board, opp_color):
        blocking_moves = []
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] != opp_color:
                    continue

                for dx, dy in directions:
                    count = 1
                    empty_spots = []

                    nx, ny = x + dx, y + dy
                    for _ in range(6):
                        if not isValidPos(nx, ny):
                            break
                        if board[nx][ny] == opp_color:
                            count += 1
                        elif board[nx][ny] == Defines.NOSTONE:
                            empty_spots.append((nx, ny))
                            break
                        else:
                            break
                        nx += dx
                        ny += dy

                    nx, ny = x - dx, y - dy
                    for _ in range(6):
                        if not isValidPos(nx, ny):
                            break
                        if board[nx][ny] == opp_color:
                            count += 1
                        elif board[nx][ny] == Defines.NOSTONE:
                            empty_spots.append((nx, ny))
                            break
                        else:
                            break
                        nx -= dx
                        ny -= dy

                    if count >= 4 and len(empty_spots) >= 1:
                        for spot in empty_spots:
                            for nx in range(max(1, spot[0]-2), min(20, spot[0]+3)):
                                for ny in range(max(1, spot[1]-2), min(20, spot[1]+3)):
                                    if isValidPos(nx, ny) and board[nx][ny] == Defines.NOSTONE:
                                        if (nx, ny) != spot:
                                            move = StoneMove()
                                            move.positions[0] = Position(
                                                spot[0], spot[1])
                                            move.positions[1] = Position(
                                                nx, ny)
                                            blocking_moves.append(move)

        return blocking_moves

    def _find_attacking_moves(self, board, color):
        return []

    def _find_tactical_moves(self, board):
        moves = []
        candidates = set()

        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] != Defines.NOSTONE:
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if isValidPos(nx, ny) and board[nx][ny] == Defines.NOSTONE:
                                candidates.add((nx, ny))

        if not candidates:
            for x in range(8, 13):
                for y in range(8, 13):
                    candidates.add((x, y))

        candidate_list = list(candidates)
        random.shuffle(candidate_list)

        for i in range(min(20, len(candidate_list))):
            for j in range(i+1, min(i+20, len(candidate_list))):
                move = StoneMove()
                move.positions[0] = Position(
                    candidate_list[i][0], candidate_list[i][1])
                move.positions[1] = Position(
                    candidate_list[j][0], candidate_list[j][1])
                moves.append(move)
                if len(moves) >= 40:
                    return moves

        return moves

    def _get_default_move(self):
        move = StoneMove()
        move.positions[0] = Position(10, 10)
        move.positions[1] = Position(10, 11)
        return move

        try:
            with open("/tmp/connect6_debug.txt", "a") as f:
                f.write(
                    f"{time.time()}: generate_moves RETURNING {len(unique_moves)} moves\n")
                f.flush()
        except:
            pass
