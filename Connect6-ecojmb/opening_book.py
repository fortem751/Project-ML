

from defines import *
import random

# Opening book using Joseki-like patterns


class OpeningBook:

    def __init__(self):
        self.book = self._initialize_book()
        self.variation_played = {}  # Track what we've played

    def _initialize_book(self):

        book = {}

        # BLACK'S first move(single stone)

        book['start_black'] = [
            ((10, 10), None, 100, "Tengen - standard opening")
        ]

        #  WHITE'S first response
        tengen_hash = self._hash_position([(10, 10, Defines.BLACK)])

        book[tengen_hash] = [
            # Diagonal approach - most flexible
            ((9, 9), (11, 11), 95, "Double diagonal - flexible"),
            ((9, 11), (11, 9), 90, "Anti-diagonal - balanced"),

            # Knight's move approach - solid
            ((8, 9), (12, 11), 85, "Large knight - spacious"),
            ((9, 8), (11, 12), 85, "Large knight variation"),

            # One-space jump - aggressive
            ((10, 8), (10, 12), 80, "Vertical split"),
            ((8, 10), (12, 10), 80, "Horizontal split"),

            # Nearby diagonals - fighting style
            ((9, 10), (11, 10), 75, "Side contact"),
            ((10, 9), (10, 11), 75, "Vertical contact"),
        ]

        # BLACK'S Second move after standard responses
        #
        pos_after_diag = [(10, 10, Defines.BLACK),
                          (9, 9, Defines.WHITE), (11, 11, Defines.WHITE)]
        diag_hash = self._hash_position(pos_after_diag)

        book[diag_hash] = [
            # Build thickness
            ((11, 9), (9, 11), 90, "Cross formation - strong"),
            ((10, 8), (8, 10), 85, "Build territory"),
            ((12, 10), (10, 12), 85, "Outer influence"),

            # Attack
            ((11, 10), (10, 11), 80, "Direct pressure"),
            ((9, 10), (10, 9), 80, "Surround center"),
        ]

        # Openng principles
        self.opening_principles = {
            'avoid_edge': True,      # Don't play on edges in opening
            'maintain_distance': 2,  # Keep at least 2 spaces between groups
            'prefer_center': True,   # Prefer moves near center
            'build_thickness': True,  # Create strong shapes
            'max_opening_moves': 6,  # Use book for first 6 moves
        }

        return book
    # Create a simple hash of stone positions

    def _hash_position(self, stones):

        # Sort by position for consistency
        sorted_stones = sorted(stones, key=lambda s: (s[0], s[1], s[2]))
        return str(sorted_stones)

    def get_book_move(self, board, color, move_number):

        # Only use book in opening
        if move_number > self.opening_principles['max_opening_moves']:
            return None, None, False

        # Don't use book if there are many stones (not an opening position)
        stone_count = sum(1 for i in range(1, 20) for j in range(1, 20)
                          if board[i][j] != Defines.NOSTONE)
        if stone_count > 10:  # Too many stones for opening book
            return None, None, False

        # Black's first move (single stone)
        if color == Defines.BLACK and self._is_empty_board(board):
            move_data = self.book['start_black'][0]
            return move_data[0], move_data[1], True

        # Extract current position
        stones = self._extract_stones(board)
        pos_hash = self._hash_position(stones)

        # Check if position is in book
        if pos_hash in self.book:
            moves = self.book[pos_hash]

            # Pick a move we haven't played too often (variation)
            move_scores = []
            for i, (pos1, pos2, score, comment) in enumerate(moves):
                # Reduce score if we've played this variation many times
                play_count = self.variation_played.get(pos_hash + str(i), 0)
                adjusted_score = score - play_count * 10
                move_scores.append((i, adjusted_score, pos1, pos2))

            # Sort by adjusted score
            move_scores.sort(key=lambda x: x[1], reverse=True)

            # Pick top move with some randomization
            if len(move_scores) > 0:

                if len(move_scores) > 1 and random.random() < 0.2:
                    chosen = move_scores[1]
                else:
                    chosen = move_scores[0]

                idx, _, pos1, pos2 = chosen

                key = pos_hash + str(idx)
                self.variation_played[key] = self.variation_played.get(
                    key, 0) + 1

                return pos1, pos2, True

        if move_number <= 4:
            return self._generate_principle_move(board, color)

        return None, None, False

    def _is_empty_board(self, board):

        for i in range(1, 20):
            for j in range(1, 20):
                if board[i][j] != Defines.NOSTONE:
                    return False
        return True

    def _extract_stones(self, board):

        stones = []
        for i in range(1, 20):
            for j in range(1, 20):
                if board[i][j] != Defines.NOSTONE:
                    stones.append((i, j, board[i][j]))
        return stones

    def _generate_principle_move(self, board, color):

        # Find existing stones
        our_stones = []
        opp_stones = []
        opponent = Defines.BLACK if color == Defines.WHITE else Defines.WHITE

        for i in range(1, 20):
            for j in range(1, 20):
                if board[i][j] == color:
                    our_stones.append((i, j))
                elif board[i][j] == opponent:
                    opp_stones.append((i, j))

        # Generate candidate positions
        candidates = []

        # Near our stones (2-3 spaces away)
        for ox, oy in our_stones:
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if abs(dx) + abs(dy) < 2:  # Too close
                        continue
                    if abs(dx) + abs(dy) > 5:  # Too far
                        continue

                    nx, ny = ox + dx, oy + dy
                    if 1 <= nx <= 19 and 1 <= ny <= 19:
                        if board[nx][ny] == Defines.NOSTONE:
                            center_dist = abs(nx - 10) + abs(ny - 10)
                            score = 50 - center_dist
                            candidates.append((nx, ny, score))

        # Near opponent stones (respond)
        for ox, oy in opp_stones:
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx == 0 and dy == 0:
                        continue

                    nx, ny = ox + dx, oy + dy
                    if 1 <= nx <= 19 and 1 <= ny <= 19:
                        if board[nx][ny] == Defines.NOSTONE:
                            score = 40
                            candidates.append((nx, ny, score))

        # If no candidates, play near center
        if not candidates:
            for x in range(8, 13):
                for y in range(8, 13):
                    if board[x][y] == Defines.NOSTONE:
                        center_dist = abs(x - 10) + abs(y - 10)
                        score = 50 - center_dist
                        candidates.append((x, y, score))

        # Remove duplicates and sort
        unique_candidates = {}
        for x, y, score in candidates:
            key = (x, y)
            if key not in unique_candidates or unique_candidates[key] < score:
                unique_candidates[key] = score

        sorted_candidates = sorted(unique_candidates.items(),
                                   key=lambda x: x[1], reverse=True)

        # Pick top two positions
        if len(sorted_candidates) >= 2:
            pos1 = sorted_candidates[0][0]
            pos2 = sorted_candidates[1][0]
            return pos1, pos2, True
        elif len(sorted_candidates) == 1:
            pos1 = sorted_candidates[0][0]
            # Find second position near first
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    x2, y2 = pos1[0] + dx, pos1[1] + dy
                    if (1 <= x2 <= 19 and 1 <= y2 <= 19 and
                            board[x2][y2] == Defines.NOSTONE and (x2, y2) != pos1):
                        return pos1, (x2, y2), True

        return None, None, False

    def add_position(self, board, move, result):

        # Extract position hash
        stones = self._extract_stones(board)
        pos_hash = self._hash_position(stones)

        pass

    def save_book(self, filename='opening_book.json'):

        import json

        # Convert book to JSON-serializable format
        json_book = {}
        for key, moves in self.book.items():
            json_book[key] = [
                {
                    'pos1': move[0],
                    'pos2': move[1],
                    'score': move[2],
                    'comment': move[3]
                }
                for move in moves
            ]

        try:
            with open(filename, 'w') as f:
                json.dump(json_book, f, indent=2)
            print(f"Opening book saved to {filename}")
        except Exception as e:
            print(f"Error saving opening book: {e}")

     # Load opening book from file
    def load_book(self, filename='opening_book.json'):
        import json

        try:
            with open(filename, 'r') as f:
                json_book = json.load(f)

            # Convert back to internal format
            self.book = {}
            for key, moves in json_book.items():
                self.book[key] = [
                    (tuple(move['pos1']) if move['pos1'] else None,
                     tuple(move['pos2']) if move['pos2'] else None,
                     move['score'],
                     move['comment'])
                    for move in moves
                ]

            print(f"Opening book loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"Opening book file {filename} not found, using default")
            return False
        except Exception as e:
            print(f"Error loading opening book: {e}")
            return False
