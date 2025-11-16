import json
import os
from defines import *
from tools import log_to_file  # Use log_to_file instead of print

# Define the expected filename
OPENING_BOOK_FILE = "opening_book.json"


class OpeningBook:

    def __init__(self):
        self.book = {}
        self.moves_loaded = 0

    def load_book(self):
        # Attempts to load the opening book from a JSON file.
        if not os.path.exists(OPENING_BOOK_FILE):
            # Log to file instead of stdout
            log_to_file(
                f"Opening book file {OPENING_BOOK_FILE} not found, using default")
            self.book = {}
            return

        try:
            with open(OPENING_BOOK_FILE, 'r') as f:
                self.book = json.load(f)

            # Count the total number of entries loaded
            self.moves_loaded = len(self.book)
            # Log to file instead of stdout
            log_to_file(
                f"Successfully loaded {self.moves_loaded} entries from opening book.")

        except json.JSONDecodeError:
            log_to_file(
                f"Error: Invalid JSON format in {OPENING_BOOK_FILE}. Using default.")
            self.book = {}
        except Exception as e:
            log_to_file(
                f"An unexpected error occurred loading the book: {e}. Using default.")
            self.book = {}

    def get_move(self, key):
        """
        Retrieves a move from the book based on the given key.

        Args:
            key (str): The hash or move phase string (e.g., 'start_black').

        Returns:
            tuple: (StoneMove, score) or (None, 0)
        """

        # Check if the key exists in the loaded book
        if key in self.book:
            book_entry = self.book[key]

            if not book_entry:
                return None, 0

            # For simplicity, just pick the first move in the list
            move_string, score = book_entry[0]

            # Convert move_string back to StoneMove object
            from tools import msg2move
            book_move = msg2move(move_string)

            # Return the move and score
            return book_move, score

        return None, 0

    def _hash_position(self, board):
        """Simple placeholder hash function for opening book keys."""
        return "hash_placeholder"
