#!/usr/bin/env python
"""
Apply emergency defensive patches to make engine harder to beat
Run this script to automatically apply all patches
"""

import os
import re


def backup_file(filename):
    """Create backup of file before modifying."""
    if os.path.exists(filename):
        backup = filename + ".backup"
        with open(filename, 'r') as f:
            content = f.read()
        with open(backup, 'w') as f:
            f.write(content)
        print(f"✓ Backed up {filename} to {backup}")
        return True
    else:
        print(f"✗ File not found: {filename}")
        return False


def apply_pattern_recognition_patches():
    """Increase threat weights in pattern_recognition.py"""
    filename = "pattern_recognition.py"

    if not backup_file(filename):
        return False

    with open(filename, 'r') as f:
        content = f.read()

    # Patch 1: Increase OPEN_FOUR
    content = re.sub(
        r"'OPEN_FOUR': 1000000,",
        "'OPEN_FOUR': 5000000,      # PATCHED: Increased from 1000000",
        content
    )

    # Patch 2: Increase STRAIGHT_FOUR
    content = re.sub(
        r"'STRAIGHT_FOUR': 500000,",
        "'STRAIGHT_FOUR': 2000000,   # PATCHED: Increased from 500000",
        content
    )

    # Patch 3: Increase OPEN_THREE
    content = re.sub(
        r"'OPEN_THREE': 50000,",
        "'OPEN_THREE': 200000,       # PATCHED: Increased from 50000",
        content
    )

    # Patch 4: Increase opponent penalty
    content = re.sub(
        r"total = our_score - opp_score \* 1\.5",
        "total = our_score - opp_score * 3.0  # PATCHED: Increased from 1.5",
        content
    )

    with open(filename, 'w') as f:
        f.write(content)

    print(f"✓ Patched {filename}")
    return True


def apply_game_engine_patches():
    """Increase search depth and time in game_engine.py"""
    filename = "game_engine.py"

    if not backup_file(filename):
        return False

    with open(filename, 'r') as f:
        content = f.read()

    # Patch 1: Increase depth
    content = re.sub(
        r"self\.m_alphabeta_depth = 5",
        "self.m_alphabeta_depth = 6  # PATCHED: Increased from 5",
        content
    )

    # Patch 2: Increase time limit
    content = re.sub(
        r"self\.m_time_limit = 5\.0",
        "self.m_time_limit = 8.0  # PATCHED: Increased from 5.0",
        content
    )

    with open(filename, 'w') as f:
        f.write(content)

    print(f"✓ Patched {filename}")
    return True


def verify_patches():
    """Verify patches were applied correctly."""
    print("\n" + "="*60)
    print("VERIFYING PATCHES")
    print("="*60)

    errors = []

    # Check pattern_recognition.py
    try:
        with open("pattern_recognition.py", 'r') as f:
            content = f.read()

        if "'OPEN_FOUR': 5000000" in content:
            print("✓ OPEN_FOUR weight increased")
        else:
            errors.append("OPEN_FOUR weight not increased")

        if "'STRAIGHT_FOUR': 2000000" in content:
            print("✓ STRAIGHT_FOUR weight increased")
        else:
            errors.append("STRAIGHT_FOUR weight not increased")

        if "opp_score * 3.0" in content:
            print("✓ Opponent penalty increased")
        else:
            errors.append("Opponent penalty not increased")

    except FileNotFoundError:
        errors.append("pattern_recognition.py not found")

    # Check game_engine.py
    try:
        with open("game_engine.py", 'r') as f:
            content = f.read()

        if "m_alphabeta_depth = 6" in content:
            print("✓ Search depth increased")
        else:
            errors.append("Search depth not increased")

        if "m_time_limit = 8.0" in content:
            print("✓ Time limit increased")
        else:
            errors.append("Time limit not increased")

    except FileNotFoundError:
        errors.append("game_engine.py not found")

    return errors


def main():
    print("="*60)
    print("EMERGENCY DEFENSIVE PATCH APPLICATION")
    print("="*60)
    print("\nThis will make the engine much more defensive:")
    print("  - 5x increase in open four threat weight")
    print("  - 4x increase in straight four threat weight")
    print("  - 4x increase in open three threat weight")
    print("  - 2x increase in opponent threat penalty")
    print("  - Deeper search (depth 6 instead of 5)")
    print("  - More time per move (8s instead of 5s)")
    print("\nBackup files will be created (.backup extension)")
    print("="*60)

    response = input("\nApply patches? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("Cancelled.")
        return

    print("\nApplying patches...")
    print("-"*60)

    success = True

    # Apply patches
    if not apply_pattern_recognition_patches():
        success = False

    if not apply_game_engine_patches():
        success = False

    if success:
        # Verify
        errors = verify_patches()

        if errors:
            print("\n⚠️  WARNINGS:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("\n" + "="*60)
            print("✓✓✓ ALL PATCHES APPLIED SUCCESSFULLY ✓✓✓")
            print("="*60)
            print("\nNext steps:")
            print("1. Rebuild: pyinstaller --onefile game_engine.py")
            print("2. Test: python quick_test.py")
            print("3. Play against Cloudict again")
            print("\nExpected improvement:")
            print("  - Engine should survive past move 10")
            print("  - Much more defensive play")
            print("  - Never misses critical threats")
    else:
        print("\n✗ Some patches failed. Check error messages above.")

    print("\nTo restore original files, rename .backup files")


if __name__ == "__main__":
    main()
