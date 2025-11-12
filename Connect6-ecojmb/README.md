# Connect 6 Engine - ECOJMB


##  Architecture Overview

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
pyinstaller --onefile --name game_engine.py

# Run
./dist/ecojmb     # Linux/Mac if name in the above command was ecojmb
dist\ecojmb.exe   # Windows
```

## Playing Against Other Engines

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










