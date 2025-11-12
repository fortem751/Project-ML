
# Smulation runner for Wumpus world with BDI agent. Main BDI cycle is implemented

import time
from wumpus_environment import WumpusWorld
from bdi_agent import BDIAgent
from visualizer import WumpusVisualizer

# Implement complete BDI reasoning cycle.


class WumpusSimulation:

    def __init__(self, world_size=4, num_pits=3, num_gold=1, max_steps=100,
                 visualize=True, step_delay=0.5):
        self.world_size = world_size
        self.num_pits = num_pits
        self.num_gold = num_gold
        self.max_steps = max_steps
        self.visualize = visualize
        self.step_delay = step_delay

        # Initialize components
        self.environment = None
        self.agent = None
        self.visualizer = None

        # Statistics
        self.stats = {
            'total_steps': 0,
            'gold_collected': 0,
            'won': False,
            'died': False,
            'reason': None
        }

    def setup(self):
        self.environment = WumpusWorld(
            self.world_size, self.num_pits, self.num_gold)
        self.agent = BDIAgent(memory_limit=5)

        if self.visualize:
            self.visualizer = WumpusVisualizer(self.world_size)

        print("="*70)
        print(" WUMPUS WORLD SIMULATION - BDI AGENT")
        print("="*70)
        print(f"World Size: {self.world_size}x{self.world_size}")
        print(f"Pits: {self.num_pits}, Gold: {self.num_gold}")
        print(f"Max Steps: {self.max_steps}")
        print("="*70)

    def run_single_simulation(self):
        self.setup()
        step = 0

        # Initial perception
        perception = self.environment.get_perception()
        self.agent.perceive(perception, self.environment)

        # Visualize initial state
        if self.visualize:
            self.visualizer.visualize_world(self.environment, self.agent, step)
            time.sleep(self.step_delay)

        print(f"\n{'='*70}")
        print(f"Starting BDI Reasoning Cycle...")
        print(f"{'='*70}\n")

        # Main BDI loop
        while step < self.max_steps and not self.environment.is_game_over():
            step += 1

            print(f"\n--- STEP {step} ---")
            print(f"Position: {self.agent.beliefs['current_position']}")

            # === BDI CYCLE ===

            # 1. DELIBERATE: Choose intention based on beliefs and desires
            print(f"\n DELIBERATE:")
            print(f"   Current Desires: {self.agent.get_current_desires()}")
            intention = self.agent.deliberate()
            print(f"   Selected Intention: {intention}")

            # 2. EXECUTE: Perform action based on intention
            print(f"\n EXECUTE:")
            action = self.agent.execute(self.environment)
            print(f"   Action: {action}")

            # 3. Perform action in environment
            if action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                success, perception = self.environment.move_agent(action)
                if success:
                    self.agent.update_position(self.environment.agent_pos)
            elif action == 'GRAB':
                self.environment.grab_gold()
            elif action == 'CLIMB':
                if self.environment.agent_pos == [0, 0]:
                    print(" Agent successfully climbed out!")
                    self.environment.won = True
                    self.environment.game_over = True
            elif action == 'SHOOT':
                # Not implemented in this version
                pass
            else:
                # WAIT or unknown action
                perception = self.environment.get_perception()

            # 4. PERCEIVE: Update beliefs based on new perceptions
            print(f"\n  PERCEIVE:")
            perception = self.environment.get_perception()
            print(f"   {perception}")
            self.agent.perceive(perception, self.environment)

            # Print belief summary
            beliefs = self.agent.get_beliefs_summary()
            print(f"\n Belief Summary:")
            print(f"   Visited cells: {beliefs['visited']}")
            print(f"   Known safe cells: {beliefs['safe_known']}")
            print(f"   Suspected pits: {beliefs['suspected_pits']}")
            print(f"   Suspected wumpus: {beliefs['suspected_wumpus']}")
            print(f"   Gold collected: {beliefs['gold_collected']}")

            # Visualize
            if self.visualize:
                self.visualizer.visualize_world(
                    self.environment, self.agent, step)
                time.sleep(self.step_delay)

            # Check game over conditions
            if self.environment.is_game_over():
                if self.environment.is_won():
                    print("\n🎉🎉🎉 VICTORY! 🎉🎉🎉")
                    self.stats['won'] = True
                    self.stats['reason'] = "All gold collected and returned home"
                else:
                    print("\n💀 GAME OVER 💀")
                    self.stats['died'] = True
                    if self.environment.agent_pos in self.environment.pit_positions:
                        self.stats['reason'] = "Fell into pit"
                    elif self.environment.agent_pos == self.environment.wumpus_pos:
                        self.stats['reason'] = "Killed by Wumpus"
                break

        # Check timeout
        if step >= self.max_steps and not self.environment.is_game_over():
            print(
                f"\n Simulation ended: Maximum steps ({self.max_steps}) reached")
            self.stats['reason'] = "Timeout"

        # Collect statistics
        self.stats['total_steps'] = step
        self.stats['gold_collected'] = self.environment.gold_collected

        # Final summary
        print(f"\n{'='*70}")
        print("SIMULATION SUMMARY")
        print(f"{'='*70}")
        print(f"Total Steps: {self.stats['total_steps']}")
        print(
            f"Gold Collected: {self.stats['gold_collected']}/{self.environment.total_gold}")
        print(f"Visited Cells: {len(self.agent.beliefs['visited_cells'])}")
        print(f"Result: {self.stats['reason']}")
        print(f"{'='*70}")

        if self.visualize:
            self.visualizer.show()

        return self.stats

    def close(self):
        if self.visualizer:
            self.visualizer.close()


class MultipleSimulationEvaluator:

    def __init__(self, num_simulations=10, world_configs=None):
        self.num_simulations = num_simulations
        self.world_configs = world_configs or [
            {'size': 4, 'pits': 3, 'gold': 1},
            {'size': 4, 'pits': 2, 'gold': 2},
            {'size': 5, 'pits': 4, 'gold': 1},
        ]
        self.results = []
    # Run multiple simulation siwth different configurations

    def run_evaluation(self, visualize_first=True):
        print("\n" + "="*70)
        print(" STARTING MULTIPLE SIMULATION EVALUATION")
        print("="*70)
        print(f"Number of simulations: {self.num_simulations}")
        print(f"Configurations: {len(self.world_configs)}")
        print("="*70 + "\n")

        for sim_num in range(self.num_simulations):
            # Rotate through configurations
            config = self.world_configs[sim_num % len(self.world_configs)]

            print(f"\n{'#'*70}")
            print(f"SIMULATION {sim_num + 1}/{self.num_simulations}")
            print(
                f"Config: Size={config['size']}, Pits={config['pits']}, Gold={config['gold']}")
            print(f"{'#'*70}")

            # Visualize only the first simulation
            visualize = visualize_first and sim_num == 0

            simulation = WumpusSimulation(
                world_size=config['size'],
                num_pits=config['pits'],
                num_gold=config['gold'],
                max_steps=100,
                visualize=visualize,
                step_delay=0.3 if visualize else 0
            )

            stats = simulation.run_single_simulation()
            stats['config'] = config
            stats['simulation_num'] = sim_num + 1
            self.results.append(stats)

            simulation.close()

            time.sleep(0.5)

        # Print overall evaluation
        self._print_evaluation()

    # PRint evaluation results and metrics
    def _print_evaluation(self):
        print("\n" + "="*70)
        print(" EVALUATION RESULTS")
        print("="*70)

        # Calculate metrics
        total_simulations = len(self.results)
        wins = sum(1 for r in self.results if r['won'])
        deaths = sum(1 for r in self.results if r['died'])
        timeouts = total_simulations - wins - deaths

        avg_steps = sum(r['total_steps']
                        for r in self.results) / total_simulations
        avg_gold = sum(r['gold_collected']
                       for r in self.results) / total_simulations

        success_rate = (wins / total_simulations) * 100
        death_rate = (deaths / total_simulations) * 100
        timeout_rate = (timeouts / total_simulations) * 100

        print(f"\nOverall Performance:")
        print(f"  Total Simulations: {total_simulations}")
        print(f"  Wins: {wins} ({success_rate:.1f}%)")
        print(f"  Deaths: {deaths} ({death_rate:.1f}%)")
        print(f"  Timeouts: {timeouts} ({timeout_rate:.1f}%)")
        print(f"\nAverage Metrics:")
        print(f"  Steps per simulation: {avg_steps:.1f}")
        print(f"  Gold collected per simulation: {avg_gold:.1f}")

        # Detailed results
        print(f"\nDetailed Results:")
        print(f"{'Sim':<5} {'Config':<20} {'Steps':<8} {'Gold':<6} {'Result':<15}")
        print("-" * 70)
        for r in self.results:
            config_str = f"{r['config']['size']}x{r['config']['size']}, P:{r['config']['pits']}, G:{r['config']['gold']}"
            result_str = "WIN" if r['won'] else "DEATH" if r['died'] else "TIMEOUT"
            print(f"{r['simulation_num']:<5} {config_str:<20} {r['total_steps']:<8} "
                  f"{r['gold_collected']:<6} {result_str:<15}")

        print("="*70)

        # Save results to file
        self._save_results()

    # Save simulationEvaluation to a text file
    def _save_results(self):
        with open('evaluation_results.txt', 'w') as f:
            f.write("WUMPUS WORLD BDI AGENT - EVALUATION RESULTS\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Total Simulations: {len(self.results)}\n")
            f.write(f"Configurations tested: {len(self.world_configs)}\n\n")

            f.write("Results:\n")
            f.write("-" * 70 + "\n")
            for r in self.results:
                f.write(f"\nSimulation {r['simulation_num']}:\n")
                f.write(f"  Config: {r['config']}\n")
                f.write(f"  Steps: {r['total_steps']}\n")
                f.write(f"  Gold Collected: {r['gold_collected']}\n")
                f.write(f"  Result: {r['reason']}\n")

        print("\n Results saved to: evaluation_results.txt")
