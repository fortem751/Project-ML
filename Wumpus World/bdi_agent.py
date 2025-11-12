"""
BDI Agent - Implements Belief-Desire-Intention architecture
"""

import random
from collections import deque


class Predicate:

    def __init__(self, name, params=None, value=None):
        self.name = name
        self.params = params or {}
        self.value = value
        self.timestamp = 0

    def __repr__(self):
        if self.params:
            params_str = ", ".join(
                [f"{k}={v}" for k, v in self.params.items()])
            return f"{self.name}({params_str})"
        return self.name

    def __eq__(self, other):
        return (self.name == other.name and
                self.params == other.params)

    def __hash__(self):
        return hash((self.name, tuple(sorted(self.params.items()))))


class Plan:

    def __init__(self, name, action, priority=1):
        self.name = name
        self.action = action  # Function to execute
        self.priority = priority

    def __repr__(self):
        return f"Plan({self.name}, priority={self.priority})"


class BDIAgent:

    def __init__(self, memory_limit=5):
        # === BELIEFS ===
        self.beliefs = {
            'current_position': [0, 0],
            'visited_cells': set([(0, 0)]),
            'safe_cells': set([(0, 0)]),
            'suspected_pits': set(),
            'suspected_wumpus': set(),
            'gold_locations': set(),
            'wumpus_alive': True,
            'has_arrow': True,
            'gold_collected': 0
        }

        # Limited memory for recent perceptions (as per requirements)
        self.memory_limit = memory_limit
        self.recent_perceptions = deque(maxlen=memory_limit)

        # DESIRES
        self.desires = set()
        self.add_desire('patrol')  # Initial desire to explore

        # INTENTIONS
        self.current_intention = None
        self.intention_stack = []

        # Movement history for reactive avoidance
        self.last_move = None
        self.move_history = []

        # Plans available to the agent
        self.plans = {}
        self._initialize_plans()

    def _initialize_plans(self):
        self.plans = {
            'patrol': Plan('patrol', self.plan_patrol, priority=1),
            'collect_gold': Plan('collect_gold', self.plan_collect_gold, priority=5),
            'avoid_pit': Plan('avoid_pit', self.plan_avoid_danger, priority=10),
            'avoid_wumpus': Plan('avoid_wumpus', self.plan_avoid_danger, priority=10),
            'search_gold': Plan('search_gold', self.plan_search_gold, priority=3),
            'return_home': Plan('return_home', self.plan_return_home, priority=2)
        }

    def add_desire(self, desire_name):
        self.desires.add(desire_name)
        print(f"🎯 Desire added: {desire_name}")

    def remove_desire(self, desire_name):
        if desire_name in self.desires:
            self.desires.remove(desire_name)
            print(f"✓ Desire fulfilled: {desire_name}")

    def perceive(self, perception, environment):
        current_pos = tuple(self.beliefs['current_position'])

        # Store perception in limited memory
        self.recent_perceptions.append({
            'position': current_pos,
            'perception': perception
        })

        # Update beliefs based on current perception
        if perception.glitter:
            # Gold detected at current position
            self.beliefs['gold_locations'].add(current_pos)
            predicate = Predicate('gold_detected', {'position': current_pos})
            print(f"✨ Perception: GLITTER at {current_pos}")

            # Change desire to collect gold
            self.add_desire('collect_gold')

        if perception.breeze:
            # Pit nearby - mark adjacent cells as suspected
            print(f"💨 Perception: BREEZE at {current_pos}")
            adjacent = self._get_adjacent_positions(current_pos)
            for adj_pos in adjacent:
                if adj_pos not in self.beliefs['visited_cells']:
                    self.beliefs['suspected_pits'].add(adj_pos)

            # Trigger reactive avoidance if breeze detected
            self.add_desire('avoid_pit')

        if perception.stench:
            # Wumpus nearby - mark adjacent cells as suspected
            print(f" Perception: STENCH at {current_pos}")
            adjacent = self._get_adjacent_positions(current_pos)
            for adj_pos in adjacent:
                if adj_pos not in self.beliefs['visited_cells']:
                    self.beliefs['suspected_wumpus'].add(adj_pos)

            # Trigger reactive avoidance
            self.add_desire('avoid_wumpus')

        if perception.scream:
            # Wumpus killed
            self.beliefs['wumpus_alive'] = False
            self.beliefs['suspected_wumpus'].clear()
            print(f" Wumpus killed! All stench areas now safe.")

        # If no danger detected, mark adjacent cells as safe
        if not perception.breeze and not perception.stench:
            adjacent = self._get_adjacent_positions(current_pos)
            for adj_pos in adjacent:
                # Only if within bounds
                if self._is_valid_position(adj_pos, environment.size):
                    self.beliefs['safe_cells'].add(adj_pos)

        # Mark current position as visited and safe
        self.beliefs['visited_cells'].add(current_pos)
        self.beliefs['safe_cells'].add(current_pos)

    def deliberate(self):

        # Highest priority: Avoid immediate danger
        if 'avoid_pit' in self.desires or 'avoid_wumpus' in self.desires:
            self.current_intention = self.plans['avoid_pit']
            return self.current_intention

        # High priority: Collect gold if detected
        if 'collect_gold' in self.desires:
            if self.beliefs['gold_locations']:
                self.current_intention = self.plans['collect_gold']
                return self.current_intention
            else:
                # Gold collected or lost
                self.remove_desire('collect_gold')

        # Medium priority: Search for gold if glitter was recently perceived
        recent_glitter = any(p['perception'].glitter for p in list(self.recent_perceptions)[-2:]
                             if self.recent_perceptions)
        if recent_glitter and not self.beliefs['gold_locations']:
            self.current_intention = self.plans['search_gold']
            return self.current_intention

        # Low priority: Return home if gold collected
        if self.beliefs['gold_collected'] > 0:
            self.add_desire('return_home')
            self.current_intention = self.plans['return_home']
            return self.current_intention

        # Default: Patrol/explore
        if 'patrol' in self.desires:
            self.current_intention = self.plans['patrol']
            return self.current_intention

        return None

    def execute(self, environment):
        if self.current_intention is None:
            return 'WAIT'

        # Execute the plan's action function
        action = self.current_intention.action(environment)

        # Store last move for reactive behavior
        if action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            self.last_move = action
            self.move_history.append(action)

        return action

    # === PLAN IMPLEMENTATIONS ===

    def plan_patrol(self, environment):
        current_pos = tuple(self.beliefs['current_position'])

        # Find safe unvisited adjacent cells
        adjacent = self._get_adjacent_positions(current_pos)
        safe_unvisited = [pos for pos in adjacent
                          if pos in self.beliefs['safe_cells']
                          and pos not in self.beliefs['visited_cells']
                          and self._is_valid_position(pos, environment.size)]

        if safe_unvisited:
            # Move to safe unvisited cell
            target = random.choice(safe_unvisited)
            return self._get_direction_to(current_pos, target)

        # No safe unvisited cells, try any safe cell
        safe_cells = [pos for pos in adjacent
                      if pos in self.beliefs['safe_cells']
                      and self._is_valid_position(pos, environment.size)]

        if safe_cells:
            target = random.choice(safe_cells)
            return self._get_direction_to(current_pos, target)

        # Random move as last resort
        return random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

    def plan_collect_gold(self, environment):

        current_pos = tuple(self.beliefs['current_position'])

        # If gold at current position, grab it
        if current_pos in self.beliefs['gold_locations']:
            self.beliefs['gold_locations'].remove(current_pos)
            self.beliefs['gold_collected'] += 1
            self.remove_desire('collect_gold')
            return 'GRAB'

        # Move towards known gold location
        if self.beliefs['gold_locations']:
            gold_pos = list(self.beliefs['gold_locations'])[0]
            direction = self._get_direction_to(current_pos, gold_pos)
            return direction

        return 'WAIT'

    def plan_search_gold(self, environment):
        current_pos = tuple(self.beliefs['current_position'])

        # Get recent positions where glitter was perceived
        glitter_positions = [p['position'] for p in list(self.recent_perceptions)[-3:]
                             if p['perception'].glitter]

        if glitter_positions:
            # Move around the glitter area
            target_area = glitter_positions[0]
            adjacent = self._get_adjacent_positions(target_area)
            safe_adjacent = [pos for pos in adjacent
                             if pos in self.beliefs['safe_cells']
                             and self._is_valid_position(pos, environment.size)]

            if safe_adjacent:
                target = random.choice(safe_adjacent)
                return self._get_direction_to(current_pos, target)

        # Random movement
        return random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

    def plan_avoid_danger(self, environment):
        if self.last_move and len(self.move_history) > 1:
            # Undo last move by going opposite direction (only if we've moved at least once)
            opposite = {
                'UP': 'DOWN',
                'DOWN': 'UP',
                'LEFT': 'RIGHT',
                'RIGHT': 'LEFT'
            }

            print(
                f"⚠️  Danger detected! Reversing last move: {self.last_move} -> {opposite[self.last_move]}")

            # Remove danger desires after reacting
            self.desires.discard('avoid_pit')
            self.desires.discard('avoid_wumpus')

            return opposite[self.last_move]

        # If no last move (first position), clear danger desires and patrol instead
        self.desires.discard('avoid_pit')
        self.desires.discard('avoid_wumpus')

        # Try to move to known safe cells first
        current_pos = tuple(self.beliefs['current_position'])
        adjacent = self._get_adjacent_positions(current_pos)
        safe_cells = [pos for pos in adjacent
                      if pos in self.beliefs['safe_cells']
                      and self._is_valid_position(pos, environment.size)]

        if safe_cells:
            target = random.choice(safe_cells)
            return self._get_direction_to(current_pos, target)

        # If no known safe cells, explore unsuspected cells (calculated risk)
        unsuspected = [pos for pos in adjacent
                       if pos not in self.beliefs['suspected_pits']
                       and pos not in self.beliefs['suspected_wumpus']
                       and self._is_valid_position(pos, environment.size)
                       and pos not in self.beliefs['visited_cells']]

        if unsuspected:
            target = random.choice(unsuspected)
            print(
                f" Taking calculated risk: exploring unsuspected cell {target}")
            return self._get_direction_to(current_pos, target)

        # Last resort: random move
        possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        return random.choice(possible_moves)

    def plan_return_home(self, environment):

        current_pos = tuple(self.beliefs['current_position'])
        home = (0, 0)

        if current_pos == home:
            self.remove_desire('return_home')
            return 'CLIMB'

        # Simple pathfinding towards home
        direction = self._get_direction_to(current_pos, home)
        return direction

    def _get_adjacent_positions(self, pos):
        x, y = pos
        return [
            (x, y+1),  # RIGHT
            (x, y-1),  # LEFT
            (x+1, y),  # DOWN
            (x-1, y)   # UP
        ]

    def _is_valid_position(self, pos, grid_size):
        x, y = pos
        return 0 <= x < grid_size and 0 <= y < grid_size

    def _get_direction_to(self, current, target):
        cx, cy = current
        tx, ty = target

        if tx < cx:
            return 'UP'
        elif tx > cx:
            return 'DOWN'
        elif ty < cy:
            return 'LEFT'
        elif ty > cy:
            return 'RIGHT'

        return 'WAIT'

    def update_position(self, new_position):
        self.beliefs['current_position'] = list(new_position)

    def get_beliefs_summary(self):
        return {
            'position': self.beliefs['current_position'],
            'visited': len(self.beliefs['visited_cells']),
            'safe_known': len(self.beliefs['safe_cells']),
            'suspected_pits': len(self.beliefs['suspected_pits']),
            'suspected_wumpus': len(self.beliefs['suspected_wumpus']),
            'gold_known': len(self.beliefs['gold_locations']),
            'gold_collected': self.beliefs['gold_collected']
        }

    def get_current_desires(self):
        return list(self.desires)

    def get_current_intention(self):
        return self.current_intention.name if self.current_intention else None
