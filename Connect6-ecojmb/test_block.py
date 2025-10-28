from defines import *
from tools import init_board, msg2move, make_move
from search_engine import SearchEngine

board = [[0] * Defines.GRID_NUM for _ in range(Defines.GRID_NUM)]
init_board(board)

# White has 5 in a row - MUST block!
for i in range(5):
    board[10][10 + i] = Defines.WHITE

engine = SearchEngine()
engine.before_search(board, Defines.BLACK, 3)
engine.move_number = 5

best_move = StoneMove()
engine.iterative_deepening_search(3, 3.0, Defines.BLACK, best_move)

pos1 = (best_move.positions[0].x, best_move.positions[0].y)
pos2 = (best_move.positions[1].x, best_move.positions[1].y)

print(f"Engine plays: {pos1}, {pos2}")
print(f"Expected: (10,15) or (10,9)")

blocks = (pos1 == (10, 15) or pos1 == (10, 9)
          or pos2 == (10, 15) or pos2 == (10, 9))
if blocks:
    print("✓ BLOCKS CORRECTLY!")
else:
    print("✗ FAILED TO BLOCK!")
