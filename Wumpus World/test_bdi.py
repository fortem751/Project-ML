
# Test script to verify BDI Agent implementation"

from wumpus_environment import WumpusWorld, Perception
from bdi_agent import BDIAgent, Predicate


def test_environment():
    print("Testing Environment...")
    env = WumpusWorld(size=4, num_pits=2, num_gold=1)

    assert env.size == 4
    assert len(env.pit_positions) == 2
    assert len(env.gold_positions) == 1
    assert env.agent_pos == [0, 0]

    # Test perception
    perception = env.get_perception()
    assert isinstance(perception, Perception)

    print(" Environment tests passed")


def test_bdi_agent():

    print("\nTesting BDI Agent...")
    agent = BDIAgent(memory_limit=5)

    # Test beliefs
    assert 'current_position' in agent.beliefs
    assert 'visited_cells' in agent.beliefs
    assert 'safe_cells' in agent.beliefs

    # Test desires
    assert 'patrol' in agent.desires

    # Test plans
    assert 'patrol' in agent.plans
    assert 'collect_gold' in agent.plans
    assert 'avoid_pit' in agent.plans

    print("✓ BDI Agent tests passed")


def test_perception():
    print("\nTesting Perception Processing...")

    env = WumpusWorld(size=4, num_pits=2, num_gold=1)
    agent = BDIAgent()

    # Get and process perception
    perception = env.get_perception()
    agent.perceive(perception, env)

    # Agent should have updated beliefs
    assert (0, 0) in agent.beliefs['visited_cells']
    assert (0, 0) in agent.beliefs['safe_cells']

    print("✓ Perception tests passed")


def test_deliberation():
    print("\nTesting Deliberation...")

    agent = BDIAgent()

    # Test with patrol desire
    intention = agent.deliberate()
    assert intention is not None
    assert intention.name == 'patrol'

    # Test with collect_gold desire
    agent.add_desire('collect_gold')
    agent.beliefs['gold_locations'].add((1, 1))
    intention = agent.deliberate()
    assert intention.name == 'collect_gold'

    print("✓ Deliberation tests passed")


def test_bdi_cycle():
    print("\nTesting Complete BDI Cycle...")

    env = WumpusWorld(size=4, num_pits=2, num_gold=1)
    agent = BDIAgent()

    # Perceive
    perception = env.get_perception()
    agent.perceive(perception, env)

    # Deliberate
    intention = agent.deliberate()
    assert intention is not None

    # Execute
    action = agent.execute(env)
    assert action in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'WAIT', 'GRAB']

    print(" BDI Cycle tests passed")


def run_all_tests():
    print("\n" + "="*50)
    print("🧪 RUNNING TESTS")
    print("="*50)

    try:
        test_environment()
        test_bdi_agent()
        test_perception()
        test_deliberation()
        test_bdi_cycle()

        print("\n" + "="*50)
        print(" ALL TESTS PASSED!")
        print("="*50 + "\n")
        return True
    except AssertionError as e:
        print(f"\n TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n ERROR: {e}\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
