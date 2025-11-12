

from simulation import WumpusSimulation, MultipleSimulationEvaluator
import argparse


def run_single_demo():

    print("\n Running Single Demonstration Simulation...\n")

    simulation = WumpusSimulation(
        world_size=4,
        num_pits=3,
        num_gold=1,
        max_steps=100,
        visualize=True,
        step_delay=0.5  # Half second between steps
    )

    stats = simulation.run_single_simulation()
    simulation.close()

    return stats


def run_multiple_evaluation(num_sims=10):

    print("\n Running Multiple Simulations for Evaluation...\n")

    evaluator = MultipleSimulationEvaluator(
        num_simulations=num_sims,
        world_configs=[
            {'size': 4, 'pits': 2, 'gold': 1},
            {'size': 4, 'pits': 3, 'gold': 1},
            {'size': 4, 'pits': 3, 'gold': 2},
            {'size': 5, 'pits': 4, 'gold': 1},
            {'size': 5, 'pits': 5, 'gold': 2},
        ]
    )

    evaluator.run_evaluation(visualize_first=True)


def main():

    parser = argparse.ArgumentParser(
        description='Wumpus World BDI Agent Simulation'
    )
    parser.add_argument(
        '--mode',
        choices=['demo', 'eval'],
        default='demo',
        help='Run mode: demo (single simulation) or eval (multiple simulations)'
    )
    parser.add_argument(
        '--num-sims',
        type=int,
        default=10,
        help='Number of simulations for evaluation mode (default: 10)'
    )

    args = parser.parse_args()

    print("\n" + "="*70)
    print(" BDI AGENT IMPLEMENTATION OF THE WUMPUS WORLD ")
    print("="*70)
    print("\nThis implementation includes:")
    print("   BDI Architecture (Beliefs, Desires, Intentions)")
    print("   Perception System (Breeze, Stench, Glitter)")
    print("   Reasoning Cycle (Perceive -> Deliberate -> Execute)")
    print("   Multiple Plans (Patrol, Collect Gold, Avoid Danger)")
    print("   Limited Memory (Recent perceptions only)")
    print("   Reactive Avoidance (Undo dangerous moves)")
    print("   Visualization")
    print("="*70 + "\n")

    if args.mode == 'demo':
        run_single_demo()
    elif args.mode == 'eval':
        run_multiple_evaluation(args.num_sims)

    print("\n Simulation complete!\n")


if __name__ == "__main__":
    main()
