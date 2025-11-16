

from defines import *


def init_board(board):
    for i in range(Defines.GRID_NUM):
        for j in range(Defines.GRID_NUM):
            if i == 0 or i == Defines.GRID_NUM - 1 or j == 0 or j == Defines.GRID_NUM - 1:
                board[i][j] = Defines.EDGE
            else:
                board[i][j] = Defines.NOSTONE


def isValidPos(x, y):
    return 1 <= x < Defines.GRID_NUM - 1 and 1 <= y < Defines.GRID_NUM - 1


def make_move(board, move, color):
    if move and move.positions[0] and move.positions[1]:
        board[move.positions[0].x][move.positions[0].y] = color
        board[move.positions[1].x][move.positions[1].y] = color


def unmake_move(board, move):
    if move and move.positions[0] and move.positions[1]:
        board[move.positions[0].x][move.positions[0].y] = Defines.NOSTONE
        board[move.positions[1].x][move.positions[1].y] = Defines.NOSTONE


def is_win_by_premove(board, move):
    if not move or not move.positions[0]:
        return False

    color = board[move.positions[0].x][move.positions[0].y]
    if color == Defines.NOSTONE:
        return False

    for pos in move.positions:
        if check_win_at_position(board, pos.x, pos.y, color):
            return True

    return False


def check_win_at_position(board, x, y, color):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for dx, dy in directions:
        count = 1

        cx, cy = x + dx, y + dy
        while 1 <= cx <= 19 and 1 <= cy <= 19 and board[cx][cy] == color:
            count += 1
            cx += dx
            cy += dy

        cx, cy = x - dx, y - dy
        while 1 <= cx <= 19 and 1 <= cy <= 19 and board[cx][cy] == color:
            count += 1
            cx -= dx
            cy -= dy

        if count >= 6:
            return True

    return False


def msg2move(msg):
    if not msg or len(msg) < 2:
        return None

    msg = msg.upper().strip()

    try:
        x1_gui = ord(msg[0]) - ord('A')
        y1_gui = ord(msg[1]) - ord('A')

        if len(msg) >= 4:
            x2_gui = ord(msg[2]) - ord('A')
            y2_gui = ord(msg[3]) - ord('A')
        else:
            # Single stone - use same position
            x2_gui = x1_gui
            y2_gui = y1_gui

        # Convert GUI (0-18) to internal (1-19)
        move = StoneMove()
        move.positions[0] = Position(x1_gui + 1, y1_gui + 1)
        move.positions[1] = Position(x2_gui + 1, y2_gui + 1)
        return move

    except Exception:
        return None


def move2msg(move):
    if not move or not move.positions[0] or not move.positions[1]:
        return "JJ"  # Center position

    # Get internal coordinates (1-19) and convert to GUI (0-18)
    x1 = max(1, min(19, move.positions[0].x)) - 1
    y1 = max(1, min(19, move.positions[0].y)) - 1
    x2 = max(1, min(19, move.positions[1].x)) - 1
    y2 = max(1, min(19, move.positions[1].y)) - 1

    # Convert to characters
    char1 = chr(ord('A') + x1)
    char2 = chr(ord('A') + y1)
    char3 = chr(ord('A') + x2)
    char4 = chr(ord('A') + y2)

    # Single stone move? Return 2 characters (GUI will duplicate)
    if x1 == x2 and y1 == y2:
        return char1 + char2
    else:
        return char1 + char2 + char3 + char4


def print_board(board, preMove=None):
    try:
        with open("/tmp/connect6_board.txt", "w") as f:
            f.write("   ")
            for j in range(1, Defines.GRID_NUM - 1):
                f.write(chr(ord('A') + j - 1))
            f.write("\n")

            for i in range(1, Defines.GRID_NUM - 1):
                f.write(f"{i:2d} ")
                for j in range(1, Defines.GRID_NUM - 1):
                    if board[i][j] == Defines.BLACK:
                        f.write("X")
                    elif board[i][j] == Defines.WHITE:
                        f.write("O")
                    elif preMove and ((i == preMove.positions[0].x and j == preMove.positions[0].y) or
                                      (i == preMove.positions[1].x and j == preMove.positions[1].y)):
                        f.write("*")
                    else:
                        f.write(".")
                f.write("\n")
    except:
        pass


def log_to_file(msg):
    """Log message to debug file."""
    try:
        import time
        with open("/tmp/connect6_debug.txt", "a") as f:
            f.write(f"{time.time()}: {msg}\n")
            f.flush()
    except:
        pass
