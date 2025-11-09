# Connect 6 Engine - ECOJMB


## 🏗️ Architecture Overview

```
game_engine.py (Main Controller)
    ↓
search_engine.py (Search with all optimizations)
    ↓
├── opening_book.py (Opening database)
├── zobrist_hash.py (Transposition tables)
├── pattern_recognition.py (Tactical patterns)
├── evaluation.py (Position evaluation)
└── move_generator.py (Move ordering)
```

## 📁 File Structure

### Core Engine Files
- **game_engine.py** - Main engine, interface handler
- **search_engine.py** - Alpha-beta with PVS, null-move, LMR, aspiration
- **evaluation.py** - Pattern-based evaluation function
- **move_generator.py** - Intelligent move generation and ordering

### Advanced Components
- **opening_book.py** - Opening theory database with variations
- **zobrist_hash.py** - Zobrist hashing + transposition table
- **pattern_recognition.py** - Threat detection and tactical patterns

### Utilities
- **defines.py** - Constants and data structures
- **tools.py** - Board operations, move conversion

## 🚀 Quick Start

### Installation
```bash

#  Python 3.7+ - Required

# Test the engine
python game_engine.py
```

### Basic Usage
```bash
# Start engine
python game_engine.py

# Commands:
name          # Get engine name
new black     # Start as black
next          # Make next move
move XXXX     # Opponent moved, respond
depth 5       # Set 5 second time limit
print         # Show board
exit          # Quit
```

### Building Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build standalone executable
pyinstaller --onefile --name ecojmb game_engine.py

# Run
./dist/ecojmb     # Linux/Mac
dist\ecojmb.exe   # Windows
```

## 🎮 Playing Against Other Engines

### Configuration
For competitive play, use these settings:

```python
# In game_engine.py __init__:
self.m_alphabeta_depth = 5  # Deep search
self.m_time_limit = 5.0     # 5 seconds per move

# Adjust based on your CPU:
# Fast CPU (i7/Ryzen): depth=6, time=8.0
# Medium CPU: depth=5, time=5.0
# Slow CPU: depth=4, time=4.0
```


### Key Algorithms
- **Alpha-Beta Pruning**: Core search algorithm
- **Iterative Deepening**: Progressive depth increase
- **Transposition Tables**: Position caching
- **Principal Variation Search**: Optimized alpha-beta
- **Null-Move Pruning**: Fast position evaluation
- **Late Move Reductions**: Selective depth reduction







