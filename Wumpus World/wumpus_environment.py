# MAin Wumpus World Environment

import numpy as np
import random
from enum import Enum


class CellType(Enum):
    EMPTY = 0
    PIT = 1
    WUMPUS = 2
    GOLD = 3
    AGENT = 4

# Current perceptions


class Perception:
    def __init__(self):
        self.breeze = False      # Pit nearby
        self.stench = False      # Wumpus nearby
        self.glitter = False     # Gold in current cell
        self.bump = False        # Hit a wall
        self.scream = False      # Wumpus killed

    def __repr__(self):
        perceptions = []
        if self.breeze:
            perceptions.append("BREEZE")
        if self.stench:
            perceptions.append("STENCH")
        if self.glitter:
            perceptions.append("GLITTER")
        if self.bump:
            perceptions.append("BUMP")
        if self.scream:
            perceptions.append("SCREAM")
        return f"Perceptions: {', '.join(perceptions) if perceptions else 'None'}"


class WumpusWorld:

    def __init__(self, size=4, num_pits=3, num_gold=1):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.agent_pos = [0, 0]  # Agent starts at (0,0)
        self.initial_pos = [0, 0]
        self.wumpus_alive = True
        self.game_over = False
        self.won = False
        self.gold_collected = 0
        self.total_gold = num_gold
        self.moves_count = 0

        # Initialize world with pits, wumpus, and gold
        self._initialize_world(num_pits, num_gold)

    def _initialize_world(self, num_pits, num_gold):

        available_positions = [(i, j) for i in range(self.size)
                               for j in range(self.size) if (i, j) != (0, 0)]

        # Place Wumpus
        wumpus_pos = random.choice(available_positions)
        self.wumpus_pos = list(wumpus_pos)
        available_positions.remove(wumpus_pos)

        # Place pits
        self.pit_positions = []
        for _ in range(min(num_pits, len(available_positions))):
            pit_pos = random.choice(available_positions)
            self.pit_positions.append(list(pit_pos))
            available_positions.remove(pit_pos)

        # Place gold
        self.gold_positions = []
        for _ in range(min(num_gold, len(available_positions))):
            gold_pos = random.choice(available_positions)
            self.gold_positions.append(list(gold_pos))
            available_positions.remove(gold_pos)

    def get_perception(self):
        perception = Perception()
        x, y = self.agent_pos

        # Check for glitter (gold in current cell)
        if self.agent_pos in self.gold_positions:
            perception.glitter = True

        # Check for breeze (pit in adjacent cell)
        adjacent_cells = self._get_adjacent_cells(x, y)
        for adj_x, adj_y in adjacent_cells:
            if [adj_x, adj_y] in self.pit_positions:
                perception.breeze = True
                break

        # Check for stench (wumpus in adjacent cell)
        if self.wumpus_alive:
            for adj_x, adj_y in adjacent_cells:
                if [adj_x, adj_y] == self.wumpus_pos:
                    perception.stench = True
                    break

        return perception

    def _get_adjacent_cells(self, x, y):
        adjacent = []
        # Right, Left, Down, Up
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.size and 0 <= new_y < self.size:
                adjacent.append((new_x, new_y))

        return adjacent

    def move_agent(self, direction):

        if self.game_over:
            return False, self.get_perception()

        self.moves_count += 1
        old_pos = self.agent_pos.copy()

        # Calculate new position
        if direction == 'UP':
            self.agent_pos[0] -= 1
        elif direction == 'DOWN':
            self.agent_pos[0] += 1
        elif direction == 'LEFT':
            self.agent_pos[1] -= 1
        elif direction == 'RIGHT':
            self.agent_pos[1] += 1
        else:
            return False, self.get_perception()

        # Check boundaries
        perception = Perception()
        if (self.agent_pos[0] < 0 or self.agent_pos[0] >= self.size or
                self.agent_pos[1] < 0 or self.agent_pos[1] >= self.size):
            perception.bump = True
            self.agent_pos = old_pos  # Revert move
            return False, perception

        # Check for pit
        if self.agent_pos in self.pit_positions:
            self.game_over = True
            print(f" Agent fell into a pit at {self.agent_pos}!")
            return False, perception

        # Check for wumpus
        if self.wumpus_alive and self.agent_pos == self.wumpus_pos:
            self.game_over = True
            print(f" Agent encountered the Wumpus at {self.agent_pos}!")
            return False, perception

        # Get new perceptions
        perception = self.get_perception()
        return True, perception

    def grab_gold(self):

        if self.agent_pos in self.gold_positions:
            self.gold_positions.remove(self.agent_pos)
            self.gold_collected += 1
            print(
                f" Gold collected! Total: {self.gold_collected}/{self.total_gold}")

            # Check win condition
            if self.gold_collected == self.total_gold and self.agent_pos == self.initial_pos:
                self.won = True
                self.game_over = True
                print(" Victory! All gold collected and returned to start!")
            return True
        return False

    def shoot_arrow(self, direction):

        if not self.wumpus_alive:
            return False

        x, y = self.agent_pos

        # Calculate arrow path
        if direction == 'UP':
            target_positions = [(x-i, y)
                                for i in range(1, self.size) if x-i >= 0]
        elif direction == 'DOWN':
            target_positions = [(x+i, y)
                                for i in range(1, self.size) if x+i < self.size]
        elif direction == 'LEFT':
            target_positions = [(x, y-i)
                                for i in range(1, self.size) if y-i >= 0]
        elif direction == 'RIGHT':
            target_positions = [(x, y+i)
                                for i in range(1, self.size) if y+i < self.size]
        else:
            return False

        # Check if arrow hits wumpus
        for pos in target_positions:
            if list(pos) == self.wumpus_pos:
                self.wumpus_alive = False
                print(f" Wumpus killed at {self.wumpus_pos}!")
                return True

        return False

    def is_game_over(self):
        return self.game_over

    def is_won(self):
        return self.won

    def get_state(self):
        return {
            'agent_pos': self.agent_pos,
            'wumpus_pos': self.wumpus_pos if self.wumpus_alive else None,
            'pit_positions': self.pit_positions,
            'gold_positions': self.gold_positions,
            'size': self.size
        }
    # REset the environment

    def reset(self):
        self.__init__(self.size, len(self.pit_positions), self.total_gold)

    def get_statistics(self):
        return {
            'moves': self.moves_count,
            'gold_collected': self.gold_collected,
            'total_gold': self.total_gold,
            'won': self.won,
            'game_over': self.game_over
        }
