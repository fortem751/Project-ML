
# Transposition Table and Zobrist Hashing implementation.

import random
from defines import *  # Assuming STONE_TYPE, GRID_NUM, etc., are here

# --- Zobrist Hash Implementation (Needed for Transposition Key) ---


class ZobristHash:

    def __init__(self):
        # Initialize hash keys for every stone type, for every square
        self.piece_keys = {}
        self.side_key = random.getrandbits(64)  # Key for side to move

        # Initialize keys for all positions (i, j) and stone types (1, 2)
        for i in range(Defines.GRID_NUM):
            for j in range(Defines.GRID_NUM):
                self.piece_keys[(i, j, Defines.BLACK)] = random.getrandbits(64)
                self.piece_keys[(i, j, Defines.WHITE)] = random.getrandbits(64)

    def compute_hash(self, board, side_to_move):
        h = 0
        for i in range(1, Defines.GRID_NUM - 1):
            for j in range(1, Defines.GRID_NUM - 1):
                piece = board[i][j]
                if piece == Defines.BLACK or piece == Defines.WHITE:
                    h ^= self.piece_keys[(i, j, piece)]

        if side_to_move == Defines.BLACK:
            h ^= self.side_key

        return h

# --- Transposition Table Implementation ---


# Define the size of the transposition table (e.g., 2^20 entries)
TT_SIZE = 1048576


class TranspositionTable:

    def __init__(self):
        self.table = {}  # Using a dictionary for simplicity
        self.zobrist = ZobristHash()
        self.hits = 0
        self.misses = 0

    def clear(self):
        self.table.clear()
        self.hits = 0
        self.misses = 0

    # CRITICAL FIX: The missing lookup method
    def lookup(self, key, depth, alpha, beta):
        if key in self.table:
            entry = self.table[key]

            # 1. Check if stored depth is sufficient
            if entry['depth'] >= depth:

                # 2. Check the bounds (Value Type)
                score = entry['score']
                value_type = entry['type']

                if value_type == 'EXACT':
                    self.hits += 1
                    return entry

                if value_type == 'ALPHA' and score <= alpha:
                    # Stored value is a lower bound, but doesn't beat alpha
                    self.hits += 1
                    return entry

                if value_type == 'BETA' and score >= beta:
                    # Stored value is an upper bound, and is outside the window
                    self.hits += 1
                    return entry

            # If depth is too low or bounds don't match, treat as a miss
            self.misses += 1
            return None

        self.misses += 1
        return None

    # NOTE: Placeholder for the store method, required by search_engine.py
    def store(self, key, depth, score, move, type):

        # Simple replacement scheme (replace if depth is higher or key is new)
        if key not in self.table or depth >= self.table[key]['depth']:
            self.table[key] = {
                'depth': depth,
                'score': score,
                'move': move,
                'type': type  # 'EXACT', 'ALPHA', or 'BETA'
            }
