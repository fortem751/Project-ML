#!/usr/bin/env python
"""
Quick diagnostic test - finds what's hanging
"""

import sys
from defines import *
from tools import init_board

print("="*60)
print("QUICK DIAGNOSTIC TEST")
print("="*60)

# Test 1: Basic imports
print("\n1. Testing imports...")
try:
    from evaluation import Evaluator
    print("   ✓ Evaluator imported")
except Exception as e:
    print(f"   ✗ Evaluator failed: {e}")
    sys.exit(1)

try:
    from pattern_recognition import PatternRecognizer
    print("   ✓ PatternRecognizer imported")
except Exception as e:
    print(f"   ✗ PatternRecognizer failed: {e}")
    sys.exit(1)

try:
    from move_generator import MoveGenerator
    print("   ✓ MoveGenerator imported")
except Exception as e:
    print(f"   ✗ MoveGenerator failed: {e}")
    sys.exit(1)

try:
    from search_engine import SearchEngine
    print("   ✓ SearchEngine imported")
except Exception as e:
    print(f"   ✗ SearchEngine failed: {e}")
    sys.exit(1)

# Test 2: Create objects
print("\n2. Creating objects...")
try:
    evaluator = Evaluator()
    print("   ✓ Evaluator created")
except Exception as e:
    print(f"   ✗ Evaluator creation failed: {e}")
    sys.exit(1)

try:
    recognizer = PatternRecognizer()
    print("   ✓ PatternRecognizer created")
except Exception as e:
    print(f"   ✗ PatternRecognizer creation failed: {e}")
    sys.exit(1)

try:
    generator = MoveGenerator()
    print("   ✓ MoveGenerator created")
except Exception as e:
    print(f"   ✗ MoveGenerator creation failed: {e}")
    sys.exit(1)

try:
    engine = SearchEngine()
    print("   ✓ SearchEngine created")
except Exception as e:
    print(f"   ✗ SearchEngine creation failed: {e}")
    sys.exit(1)

# Test 3: Basic board operations
print("\n3. Testing board operations...")
try:
    board = [[0] * Defines.GRID_NUM for _ in range(Defines.GRID_NUM)]
    init_board(board)
    print("   ✓ Board initialized")
except Exception as e:
    print(f"   ✗ Board init failed: {e}")
    sys.exit(1)

# Test 4: Pattern recognition
print("\n4. Testing pattern recognition...")
try:
    board[10][10] = Defines.BLACK
    board[10][11] = Defines.BLACK
    board[10][12] = Defines.BLACK

    analysis = recognizer.analyze_position(board, Defines.BLACK)
    print(
        f"   ✓ Pattern analysis works (found {len(analysis['threats'])} threats)")
except Exception as e:
    print(f"   ✗ Pattern analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Evaluation
print("\n5. Testing evaluation...")
try:
    score = evaluator.evaluate_position(board, Defines.BLACK)
    print(f"   ✓ Evaluation works (score: {score})")
except Exception as e:
    print(f"   ✗ Evaluation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Move generation
print("\n6. Testing move generation...")
try:
    moves = generator.generate_moves(
        board, Defines.BLACK, depth=0, max_moves=10)
    print(f"   ✓ Move generation works (generated {len(moves)} moves)")
except Exception as e:
    print(f"   ✗ Move generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Simple search (VERY shallow)
print("\n7. Testing search (depth 1, may take a moment)...")
try:
    board2 = [[0] * Defines.GRID_NUM for _ in range(Defines.GRID_NUM)]
    init_board(board2)
    board2[10][10] = Defines.BLACK

    engine.before_search(board2, Defines.WHITE, 1)
    engine.move_number = 10  # Past opening book

    best_move = StoneMove()
    print("   Starting search...")

    import time
    start = time.time()
    score = engine.iterative_deepening_search(1, 2.0, Defines.WHITE, best_move)
    elapsed = time.time() - start

    print(f"   ✓ Search works (took {elapsed:.2f}s, score: {score})")
except KeyboardInterrupt:
    print("   ✗ Search HUNG (interrupted by user)")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Search failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✓ ALL BASIC TESTS PASSED")
print("="*60)
print("\nIf this passed but full test hangs, the issue is in deeper search.")
print("Try reducing search depth in full tests.")
