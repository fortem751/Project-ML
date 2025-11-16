

import random
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
import time
# Imports for evaluation
from search_engine import SearchEngine
from defines import Defines, StoneMove
from tools import init_board


@dataclass
class Individual:
    weights: Dict[str, float]
    fitness: float = 0.0
    wins: int = 0
    losses: int = 0
    draws: int = 0

    def copy(self):

        return Individual(
            weights=self.weights.copy(),
            fitness=self.fitness,
            wins=self.wins,
            losses=self.losses,
            draws=self.draws
        )


class EvolutionaryOptimizer:

    def __init__(self,
                 population_size: int = 20,
                 generations: int = 10,
                 mutation_rate: float = 0.15,
                 crossover_rate: float = 0.7,
                 elite_count: int = 2):
        """
        Args:
            population_size: Number of individuals (must be even)
            generations: Number of evolution cycles
            mutation_rate: Probability of mutating a weight
            crossover_rate: Probability of crossing over
            elite_count: Number of individuals to carry over unchanged
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_count = elite_count

        self.population: List[Individual] = []
        self.best_individual: Individual = None
        self.best_fitness: float = -float('inf')
        self.generation_stats = []

    def get_default_weights(self) -> Dict[str, float]:
        """
        Returns baseline weights for initialization.
        NOW INCLUDES ALL TACTICAL AND POSITIONAL FACTORS.
        """
        return {
            # Win/Loss threats (High values)
            'win': 10000000.0,
            'threat_win_immediate': 1000000.0,
            'threat_win_next': 50000.0,
            'threat_opponent_win': 500000.0,

            # Pattern scores (Tactical)
            'pattern_score': 1.0,
            'pattern_5_open': 100000.0,
            'pattern_5_half': 50000.0,
            'pattern_5_closed': 25000.0,
            'pattern_4_open': 10000.0,
            'pattern_4_half': 5000.0,
            'pattern_4_closed': 1000.0,
            'pattern_3_open': 500.0,
            'pattern_3_half': 200.0,
            'pattern_3_closed': 50.0,
            'pattern_2_open': 50.0,
            'pattern_2_half': 20.0,
            'pattern_2_closed': 5.0,

            # Positional & Strategic factors (Lower values)
            'center_control': 8.0,
            'mobility': 3.0,
            'connectivity': 5.0,
            'influence': 4.0,
            'tempo': 10.0,
            'development': 6.0,
        }

    def _initialize_population(self):
        """Initialize population with small variations around default weights."""
        defaults = self.get_default_weights()
        self.population = []
        for _ in range(self.population_size):
            new_weights = {}
            for key, default_value in defaults.items():
                # Add small random jitter (up to 10% for large weights, larger for small)
                jitter = default_value * \
                    random.uniform(-0.1, 0.1) if abs(
                        default_value) > 100 else random.uniform(-1.0, 1.0)
                new_weights[key] = default_value + jitter
                # Ensure winning scores stay positive and dominant
                if 'win' in key or 'threat' in key or 'pattern_5' in key:
                    new_weights[key] = max(1000, new_weights[key])

            individual = Individual(weights=new_weights)
            self.population.append(individual)

        self.best_individual = self.population[0].copy()

    def _evaluate_fitness(self, individual: Individual, opponent: Individual):
        """
        Play a fast game between two individuals and update fitness.
        Fitness is based on Elo-like score: Win (+1), Draw (+0.5), Loss (0).
        """
        # Create two search engines for the match
        engine1 = SearchEngine()
        engine2 = SearchEngine()

        # Inject weights into the evaluators
        engine1.evaluator.weights = individual.weights
        engine2.evaluator.weights = opponent.weights

        # Set fast, but focused search parameters
        search_depth = 2       # Minimal depth to learn basic threats
        time_limit = 0.1       # 100ms time limit
        max_moves = 30         # Shorter games for faster iteration

        engine1.m_max_depth = search_depth
        engine1.max_time = time_limit
        engine2.m_max_depth = search_depth
        engine2.max_time = time_limit

        # Initialize game
        board = [[0 for _ in range(Defines.GRID_NUM)]
                 for _ in range(Defines.GRID_NUM)]
        init_board(board)
        current_player = Defines.BLACK
        move_count = 0
        game_result = 0  # 0: ongoing, 1: BLACK wins, 2: WHITE wins, 3: Draw

        # CRITICAL FIX: Define a placeholder for the best move
        placeholder_best_move = StoneMove()

        # Match (Individual vs Opponent)
        for move_count in range(max_moves):
            current_engine = engine1 if current_player == Defines.BLACK else engine2

            # Get move from engine
            # CRITICAL FIX: Pass the placeholder_best_move object as the third argument
            move, score = current_engine.iterative_deepening_search(
                board,
                current_player,
                search_depth,  # <--- 3rd argument (max_depth)
                placeholder_best_move  # <--- 4th argument (best_move output)
            )

            # Apply move
            if not move or (move.positions[0].x == 0 and move.positions[0].y == 0):
                # If the search failed to return a move, it's a loss for the current player
                game_result = Defines.WHITE if current_player == Defines.BLACK else Defines.BLACK
                break

            # The move is a StoneMove object, which contains two StonePosition objects
            board[move.positions[0].x][move.positions[0].y] = current_player
            board[move.positions[1].x][move.positions[1].y] = current_player

            # Check for win condition (Connect6 checks win after the move is made)
            if current_engine.evaluator.is_win(board, current_player):
                game_result = current_player
                break

            # Switch player
            current_player = Defines.WHITE if current_player == Defines.BLACK else Defines.BLACK

        # Update fitness based on result (rest of the method unchanged)
        if game_result == Defines.BLACK:
            individual.wins += 1
            opponent.losses += 1
            individual.fitness += 1.0
            opponent.fitness += 0.0
        elif game_result == Defines.WHITE:
            individual.losses += 1
            opponent.wins += 1
            individual.fitness += 0.0
            opponent.fitness += 1.0
        else:  # Draw (max_moves reached)
            individual.draws += 1
            opponent.draws += 1
            individual.fitness += 0.5
            opponent.fitness += 0.5

    def _select(self) -> Individual:
        """Tournament Selection: Pick 3 random individuals and return the best."""
        competitors = random.sample(self.population, 3)
        return max(competitors, key=lambda x: x.fitness)

    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Single-point crossover for weights."""
        if random.random() < self.crossover_rate:
            keys = list(parent1.weights.keys())
            crossover_point = random.randint(1, len(keys) - 1)

            child1_weights = {}
            child2_weights = {}

            # Crossover
            for i, key in enumerate(keys):
                if i < crossover_point:
                    child1_weights[key] = parent1.weights[key]
                    child2_weights[key] = parent2.weights[key]
                else:
                    child1_weights[key] = parent2.weights[key]
                    child2_weights[key] = parent1.weights[key]

            return Individual(weights=child1_weights), Individual(weights=child2_weights)
        else:
            return parent1.copy(), parent2.copy()

    def _mutate(self, individual: Individual):
        """Mutate weights with small random adjustments."""
        for key, value in individual.weights.items():
            if random.random() < self.mutation_rate:
                # Mutation magnitude inversely proportional to weight magnitude
                if abs(value) > 1000:
                    delta = random.uniform(-10.0, 10.0)
                elif abs(value) > 10:
                    delta = random.uniform(-1.0, 1.0)
                else:
                    delta = random.uniform(-0.1, 0.1)

                individual.weights[key] = value + delta

                # Keep critical weights (like 'win') high and positive
                if 'win' in key or 'threat' in key or 'pattern_5' in key:
                    individual.weights[key] = max(
                        1000, individual.weights[key])

        individual.fitness = 0.0  # Reset fitness after mutation

    def evolve(self) -> Individual:
        """Run the evolutionary algorithm for all generations."""
        self._initialize_population()
        print(
            f"Starting evolution: {self.generations} generations, pop size {self.population_size}")

        for generation in range(self.generations):
            # Reset fitnesses for the new generation's evaluation
            for individual in self.population:
                individual.fitness = 0.0
                individual.wins = 0
                individual.losses = 0
                individual.draws = 0

            # 1. Tournament: Round-Robin Evaluation
            print(f"--- Generation {generation + 1}/{self.generations} ---")

            # Round-Robin: Each individual plays two games against N/2 partners
            for i in range(0, self.population_size // 2):
                p1 = self.population[i]
                p2 = self.population[i + self.population_size // 2]

                # Game 1: P1 (Black) vs P2 (White)
                self._evaluate_fitness(p1, p2)

                # Game 2: P2 (Black) vs P1 (White) - to eliminate color bias
                self._evaluate_fitness(p2, p1)

                print(
                    f"  Match {i+1}: P{i} ({p1.fitness:.2f}) vs P{i + self.population_size // 2} ({p2.fitness:.2f})")

            # 2. Selection and Elitism
            self.population.sort(key=lambda x: x.fitness, reverse=True)

            # Update overall best
            if self.population[0].fitness > self.best_fitness:
                self.best_fitness = self.population[0].fitness
                self.best_individual = self.population[0].copy()
                print(
                    f"  >> New Best Individual! Fitness: {self.best_fitness:.2f}")

            # Collect statistics
            avg_fitness = sum(
                i.fitness for i in self.population) / self.population_size
            max_fitness = self.population[0].fitness
            self.generation_stats.append({
                'generation': generation + 1,
                'max_fitness': max_fitness,
                'avg_fitness': avg_fitness,
                'best_weights': self.population[0].weights.copy()
            })
            print(
                f"  Generation Summary: Max Fitness: {max_fitness:.2f}, Avg Fitness: {avg_fitness:.2f}")

            if generation < self.generations - 1:
                # Select elites for next generation
                next_population: List[Individual] = [
                    self.population[i].copy() for i in range(self.elite_count)
                ]

                # 3. Crossover and Mutation to fill the rest of the population
                while len(next_population) < self.population_size:
                    # Select two parents using tournament selection
                    parent1 = self._select()
                    parent2 = self._select()

                    # Crossover
                    child1, child2 = self._crossover(parent1, parent2)

                    # Mutate (in-place)
                    self._mutate(child1)
                    self._mutate(child2)

                    # Add to next population
                    next_population.append(child1)
                    if len(next_population) < self.population_size:
                        next_population.append(child2)

                self.population = next_population

        return self.best_individual

    def save_results(self, filename: str = "optimized_weights.json"):
        """Save best weights and statistics"""
        results = {
            'best_weights': self.best_individual.weights,
            'best_fitness': self.best_fitness,
            'statistics': self.generation_stats,
            'parameters': {
                'population_size': self.population_size,
                'generations': self.generations,
                'mutation_rate': self.mutation_rate,
                'crossover_rate': self.crossover_rate,
                'elite_count': self.elite_count,
                'training_depth': 2,  # Patched value
                'training_time_limit': 0.1,  # Patched value
                'training_max_moves': 30  # Patched value
            }
        }

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n Results saved to {filename}")


def main():

    # Create optimizer with reasonable parameters
    optimizer = EvolutionaryOptimizer(
        population_size=20,      # 20 individuals
        generations=10,          # 10 generations (Run this once or twice)
        mutation_rate=0.15,      # 15% mutation rate
        crossover_rate=0.7,      # 70% crossover rate
        elite_count=2            # Keep top 2
    )

    # Run evolution
    best = optimizer.evolve()

    # Save results
    optimizer.save_results()

    print("\n" + "="*60)
    print("Run complete! Check 'optimized_weights.json' for results.")
    print("="*60)


if __name__ == "__main__":
    main()
