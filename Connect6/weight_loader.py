"""
Automatic Weight Loader for Connect6 Engine
Hybrid approach: Uses optimized weights if available, otherwise defaults
"""

import os
import json


def load_best_weights(json_file='optimized_weights.json', verbose=True):
    # Try to load optimized weights
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                weights = data['best_weights']

                if verbose:
                    fitness = data.get('best_fitness', 'unknown')
                    print(f" Loaded optimized weights (fitness: {fitness})")

                return weights

        except Exception as e:
            if verbose:
                print(f" Error loading optimized weights: {e}")
                print("  Falling back to default weights")

    # Fall back to default weights
    if verbose:
        print(" Using default weights (no optimization file found)")

    return get_default_weights()


def get_default_weights():
    return {
        # Win/Loss threats
        'threat_win_immediate': 1000000,
        'threat_win_next': 50000,
        'threat_opponent_win': 500000,

        # 5-in-a-row patterns
        'pattern_5_open': 100000,
        'pattern_5_half': 50000,
        'pattern_5_closed': 25000,

        # 4-in-a-row patterns
        'pattern_4_open': 10000,
        'pattern_4_half': 5000,
        'pattern_4_closed': 1000,

        # 3-in-a-row patterns
        'pattern_3_open': 500,
        'pattern_3_half': 200,
        'pattern_3_closed': 50,

        # 2-in-a-row patterns
        'pattern_2_open': 50,
        'pattern_2_half': 20,
        'pattern_2_closed': 5,
    }


def save_weights_to_engine(json_file='optimized_weights.json',
                           output_file='optimized_weights.py'):
    if not os.path.exists(json_file):
        print(f" File not found: {json_file}")
        return False

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        weights = data['best_weights']
        fitness = data.get('best_fitness', 'unknown')

        # Generate Python code
        code = f'''"""
Optimized weights from evolutionary algorithm
Fitness: {fitness}
"""

OPTIMIZED_WEIGHTS = {{
'''

        for key, value in sorted(weights.items()):
            code += f"    '{key}': {value},\n"

        code += "}\n"

        # Write to file
        with open(output_file, 'w') as f:
            f.write(code)

        print(f" Weights exported to {output_file}")
        print(f"  Fitness: {fitness}")
        print(f"\nYou can now import with:")
        print(f"  from {output_file[:-3]} import OPTIMIZED_WEIGHTS")

        return True

    except Exception as e:
        print(f" Error exporting weights: {e}")
        return False


if __name__ == "__main__":
    # Test the loader
    print("="*60)
    print("WEIGHT LOADER TEST")
    print("="*60)

    weights = load_best_weights()

    print(f"\nLoaded {len(weights)} weight parameters:")
    for key, value in sorted(weights.items()):
        print(f"  {key:25s}: {value:8.0f}")

    # Try to export if optimized weights exist
    if os.path.exists('optimized_weights.json'):
        print("\n" + "="*60)
        save_weights_to_engine()
