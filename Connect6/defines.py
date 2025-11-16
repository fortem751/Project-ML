
# Game constants and definitions.
class Defines:

    # Board size
    GRID_NUM = 21  # 19x19 board + 2 edge rows/cols

    # Stone types
    NOSTONE = 0
    BLACK = 1
    WHITE = 2
    EDGE = 3  # Edge marker

    # Engine settings
    ENGINE_NAME = "ecojmb"
    MSG_LENGTH = 256

    # Search limits
    MAX_DEPTH = 12
    INFINITY = 999999
    MAXINT = 999999
    MININT = -999999

    # Win condition
    WIN_LENGTH = 6

    # Evaluation weights
    WIN_SCORE = 100000
    LOSE_SCORE = -100000


class Position:

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Position({self.x},{self.y})"

    def copy(self):
        return Position(self.x, self.y)


class StoneMove:

    def __init__(self):
        self.positions = [Position(), Position()]

    def __repr__(self):
        return f"StoneMove({self.positions[0]}, {self.positions[1]})"

    def copy(self):

        new_move = StoneMove()
        new_move.positions[0] = Position(
            self.positions[0].x, self.positions[0].y)
        new_move.positions[1] = Position(
            self.positions[1].x, self.positions[1].y)
        return new_move
