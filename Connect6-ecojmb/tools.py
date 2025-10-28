from defines import *
import time


def isValidPos(x, y):
    return x > 0 and x < Defines.GRID_NUM - 1 and y > 0 and y < Defines.GRID_NUM - 1


def init_board(board):
    for i in range(21):
        board[i][0] = board[0][i] = board[i][Defines.GRID_NUM - 1] = board[Defines.GRID_NUM - 1][i] = Defines.BORDER
    for i in range(1, Defines.GRID_NUM - 1):
        for j in range(1, Defines.GRID_NUM - 1):
            board[i][j] = Defines.NOSTONE


def make_move(board, move, color):
    # Validate coordinates before making move
    if (1 <= move.positions[0].x <= 19 and 1 <= move.positions[0].y <= 19):
        board[move.positions[0].x][move.positions[0].y] = color
    if (1 <= move.positions[1].x <= 19 and 1 <= move.positions[1].y <= 19):
        board[move.positions[1].x][move.positions[1].y] = color


def unmake_move(board, move):
    if (1 <= move.positions[0].x <= 19 and 1 <= move.positions[0].y <= 19):
        board[move.positions[0].x][move.positions[0].y] = Defines.NOSTONE
    if (1 <= move.positions[1].x <= 19 and 1 <= move.positions[1].y <= 19):
        board[move.positions[1].x][move.positions[1].y] = Defines.NOSTONE


def is_win_by_premove(board, preMove):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for direction in directions:
        for i in range(len(preMove.positions)):
            position = preMove.positions[i]
            x = position.x
            y = position.y

            # Skip invalid positions
            if not (1 <= x <= 19 and 1 <= y <= 19):
                continue

            movStone = board[x][y]
            if movStone == Defines.BORDER or movStone == Defines.NOSTONE:
                continue

            count = 1
            temp_x, temp_y = x + direction[0], y + direction[1]
            while board[temp_x][temp_y] == movStone:
                count += 1
                temp_x += direction[0]
                temp_y += direction[1]

            temp_x, temp_y = x - direction[0], y - direction[1]
            while board[temp_x][temp_y] == movStone:
                count += 1
                temp_x -= direction[0]
                temp_y -= direction[1]

            if count >= 6:
                return True
    return False


def get_msg(max_len):
    buf = input().strip()
    return buf[:max_len]


def log_to_file(msg):
    g_log_file_name = Defines.LOG_FILE
    try:
        with open(g_log_file_name, "a") as file:
            tm = time.time()
            ptr = time.ctime(tm)
            ptr = ptr[:-1]
            file.write(f"[{ptr}] - {msg}\n")
        return 0
    except Exception as e:
        print(f"Error: Can't open log file - {g_log_file_name}")
        return -1


def move2msg(move):
    # Validate and clamp coordinates
    x1 = max(1, min(19, move.positions[0].x))
    y1 = max(1, min(19, move.positions[0].y))
    x2 = max(1, min(19, move.positions[1].x))
    y2 = max(1, min(19, move.positions[1].y))

    if x1 == x2 and y1 == y2:
        msg = f"{chr(y1 + ord('A') - 1)}{chr(ord('S') - x1 + 1)}"
        return msg
    else:
        msg = f"{chr(y1 + ord('A') - 1)}{chr(ord('S') - x1 + 1)}" \
              f"{chr(y2 + ord('A') - 1)}{chr(ord('S') - x2 + 1)}"
        return msg


def msg2move(msg):
    move = StoneMove()
    msg = msg.strip().upper()

    if len(msg) == 2:
        col = ord(msg[0]) - ord('A') + 1
        row = ord('S') - ord(msg[1]) + 1

        # Clamp to valid range [1-19]
        col = max(1, min(19, col))
        row = max(1, min(19, row))

        move.positions[0].x = row
        move.positions[0].y = col
        move.positions[1].x = row
        move.positions[1].y = col
    else:
        col1 = ord(msg[0]) - ord('A') + 1
        row1 = ord('S') - ord(msg[1]) + 1
        col2 = ord(msg[2]) - ord('A') + 1
        row2 = ord('S') - ord(msg[3]) + 1

        # Clamp all to valid range [1-19]
        col1 = max(1, min(19, col1))
        row1 = max(1, min(19, row1))
        col2 = max(1, min(19, col2))
        row2 = max(1, min(19, row2))

        move.positions[0].x = row1
        move.positions[0].y = col1
        move.positions[1].x = row2
        move.positions[1].y = col2

    move.score = 0
    return move


def print_board(board, preMove=None):
    print("   " + "".join([chr(i + ord('A') - 1) + " " for i in range(1, Defines.GRID_NUM - 1)]))
    for i in range(1, Defines.GRID_NUM - 1):
        print(f"{chr(ord('A') - 1 + i)}", end=" ")
        for j in range(1, Defines.GRID_NUM - 1):
            x = Defines.GRID_NUM - 1 - j
            y = i
            stone = board[x][y]
            if stone == Defines.NOSTONE:
                print(" -", end="")
            elif stone == Defines.BLACK:
                print(" O", end="")
            elif stone == Defines.WHITE:
                print(" *", end="")
        print(" ", end="")
        print(f"{chr(ord('A') - 1 + i)}", end="\n")
    print("   " + "".join([chr(i + ord('A') - 1) + " " for i in range(1, Defines.GRID_NUM - 1)]))


def print_score(move_list, n):
    board = [[0] * Defines.GRID_NUM for _ in range(Defines.GRID_NUM)]
    for move in move_list:
        board[move.x][move.y] = move.score

    print("  " + "".join([f"{i:4}" for i in range(1, Defines.GRID_NUM - 1)]))
    for i in range(1, Defines.GRID_NUM - 1):
        print(f"{i:2}", end="")
        for j in range(1, Defines.GRID_NUM - 1):
            score = board[i][j]
            if score == 0:
                print("   -", end="")
            else:
                print(f"{score:4}", end="")
        print()