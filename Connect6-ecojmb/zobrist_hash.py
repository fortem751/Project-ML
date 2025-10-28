"""
Zobrist Hashing for efficient transposition table lookups.
Professional-grade implementation for Connect 6.
"""

import random
from defines import *


class ZobristHash:
    """
    Zobrist hashing for board positions.
    Allows O(1) incremental hash updates and position comparison.
    """
    
    def __init__(self, seed=42):
        """Initialize Zobrist hash tables."""
        random.seed(seed)
        
        # Hash table: [x][y][color] -> random 64-bit number
        # We need hashes for BLACK and WHITE at each position
        self.hash_table = {}
        
        # Generate random hash values for each position and color
        for x in range(1, 20):
            for y in range(1, 20):
                # Black stone at (x, y)
                self.hash_table[(x, y, Defines.BLACK)] = random.getrandbits(64)
                # White stone at (x, y)
                self.hash_table[(x, y, Defines.WHITE)] = random.getrandbits(64)
        
        # Side to move hash
        self.side_to_move_hash = random.getrandbits(64)
    
    def compute_hash(self, board, color):
        """
        Compute full board hash from scratch.
        Used for initialization and verification.
        """
        hash_value = 0
        
        # XOR all stone positions
        for x in range(1, 20):
            for y in range(1, 20):
                if board[x][y] == Defines.BLACK:
                    hash_value ^= self.hash_table[(x, y, Defines.BLACK)]
                elif board[x][y] == Defines.WHITE:
                    hash_value ^= self.hash_table[(x, y, Defines.WHITE)]
        
        # Include side to move
        if color == Defines.WHITE:
            hash_value ^= self.side_to_move_hash
        
        return hash_value
    
    def update_hash(self, current_hash, x, y, color, is_place=True):
        """
        Incrementally update hash for a move.
        
        Args:
            current_hash: Current board hash
            x, y: Position
            color: Stone color
            is_place: True if placing stone, False if removing
        
        Returns:
            Updated hash
        """
        # XOR is its own inverse, so placing and removing use same operation
        return current_hash ^ self.hash_table[(x, y, color)]
    
    def toggle_side(self, current_hash):
        """Toggle side to move in hash."""
        return current_hash ^ self.side_to_move_hash


class TranspositionTable:
    """
    Professional transposition table with Zobrist hashing.
    Includes age-based replacement and proper flag handling.
    """
    
    # Entry types
    EXACT = 0      # Exact score
    LOWER_BOUND = 1  # Score is at least this (beta cutoff)
    UPPER_BOUND = 2  # Score is at most this (alpha cutoff)
    
    def __init__(self, max_size=500000):
        """
        Initialize transposition table.
        
        Args:
            max_size: Maximum number of entries
        """
        self.table = {}
        self.max_size = max_size
        self.zobrist = ZobristHash()
        self.current_age = 0
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.collisions = 0
    
    def clear(self):
        """Clear the table and increment age."""
        self.table.clear()
        self.current_age += 1
        self.hits = 0
        self.misses = 0
        self.collisions = 0
    
    def soft_clear(self):
        """
        Soft clear - only remove old entries.
        Keeps recent positions for better performance.
        """
        if len(self.table) > self.max_size * 0.8:
            # Remove entries from old ages
            to_remove = []
            for key, entry in self.table.items():
                if entry['age'] < self.current_age - 2:
                    to_remove.append(key)
            
            for key in to_remove:
                del self.table[key]
        
        self.current_age += 1
    
    def store(self, hash_key, depth, score, flag, best_move=None, threat_level=0):
        """
        Store position in transposition table.
        
        Args:
            hash_key: Zobrist hash of position
            depth: Depth of search
            score: Evaluation score
            flag: EXACT, LOWER_BOUND, or UPPER_BOUND
            best_move: Best move from this position
            threat_level: Tactical threat level (0-3)
        """
        # Check if we should replace existing entry
        if hash_key in self.table:
            old_entry = self.table[hash_key]
            
            # Always replace if:
            # 1. New depth is greater
            # 2. Same depth but newer age
            # 3. Exact score vs bound
            if (depth > old_entry['depth'] or
                (depth == old_entry['depth'] and self.current_age > old_entry['age']) or
                (flag == self.EXACT and old_entry['flag'] != self.EXACT)):
                pass  # Will replace
            else:
                return  # Keep old entry
        
        # Store new entry
        self.table[hash_key] = {
            'depth': depth,
            'score': score,
            'flag': flag,
            'best_move': best_move,
            'age': self.current_age,
            'threat_level': threat_level
        }
        
        # Clean up if table is too large
        if len(self.table) > self.max_size:
            self._cleanup()
    
    def probe(self, hash_key, depth, alpha, beta):
        """
        Probe transposition table.
        
        Args:
            hash_key: Zobrist hash
            depth: Current search depth
            alpha, beta: Current alpha-beta bounds
        
        Returns:
            (found, score, best_move) or (False, None, None)
        """
        if hash_key not in self.table:
            self.misses += 1
            return False, None, None
        
        entry = self.table[hash_key]
        
        # Entry must be from equal or greater depth
        if entry['depth'] < depth:
            self.misses += 1
            return False, None, entry.get('best_move')
        
        self.hits += 1
        score = entry['score']
        flag = entry['flag']
        
        # Check if score is usable
        if flag == self.EXACT:
            return True, score, entry.get('best_move')
        elif flag == self.LOWER_BOUND and score >= beta:
            return True, score, entry.get('best_move')
        elif flag == self.UPPER_BOUND and score <= alpha:
            return True, score, entry.get('best_move')
        
        # Entry exists but doesn't cause cutoff
        return False, None, entry.get('best_move')
    
    def get_pv_move(self, hash_key):
        """Get principal variation move if available."""
        if hash_key in self.table:
            return self.table[hash_key].get('best_move')
        return None
    
    def _cleanup(self):
        """Remove old entries when table is full."""
        # Remove oldest entries (by age)
        entries_by_age = []
        for key, entry in self.table.items():
            entries_by_age.append((key, entry['age'], entry['depth']))
        
        # Sort by age (oldest first), then by depth (shallowest first)
        entries_by_age.sort(key=lambda x: (x[1], -x[2]))
        
        # Remove oldest 20%
        remove_count = len(entries_by_age) // 5
        for i in range(remove_count):
            key = entries_by_age[i][0]
            if key in self.table:
                del self.table[key]
    
    def get_stats(self):
        """Get transposition table statistics."""
        total_queries = self.hits + self.misses
        hit_rate = self.hits / total_queries if total_queries > 0 else 0
        
        return {
            'size': len(self.table),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate * 100,
            'age': self.current_age
        }
    
    def resize(self, new_max_size):
        """Resize the transposition table."""
        self.max_size = new_max_size
        if len(self.table) > new_max_size:
            self._cleanup()