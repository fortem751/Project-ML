# TIA.Connect6 Game Engine - Ecojmb


## 📁 Project Structure

### Modular 9-File Architecture

```
TIA.Connect6/
├── game_engine_gui.py          # Main interface and protocol handling
├── search_engine.py             # Search orchestration and iterative deepening
├── evaluation.py                # Position evaluation and weight management
├── threat_detection.py          # Threat analysis and win detection
├── pattern_recognition.py       # Strategic pattern library
├── move_generator.py            # Legal move generation and ordering
├── opening_book.py              # Professional opening positions
├── transposition_table.py       # Position caching with Zobrist hashing
├── zobrist_hash.py              # Hash key generation
├── opening_book.json            # Opening book data
└── optimized_weights.json       # Evaluation weights
└── tools.py                     # Board management and move conversion utilities
└── weight_optimizer.py          # Evolutionary Algorithm for Weight Optimization
└── weight_loader.py             # Automatic Weight Loader for Connect6 Engine
```


### Installation
### Clone Repository

```bash
git clone git clone https://github.com/fortem751/Project-ML.git
cd Connect6

```bash

#  Python 3.7+ - Required

### Playing with Connect6GUI

1. **Create Engine Executable**:
   ```bash
   pyinstaller --clean --onefile --name ECOJMB \
     --hidden-import evaluation  \
     --hidden-import move_generator  \
     --add-data "optimized_weights.json:." \
     --add-data "opening_book.json:."  \
      game_engine.py
   ```
2. **Add Engine to GUI**:
   - Open Connect6GUI
   - Load Black/White 
   - Select ecojmb as player (from dist folder in the same directory where game engine was run)

3. **Start Playing!**
   - Choose Human vs AI or AI vs AI
   - Engine appears as "Ecojmb" in player selection

### Command Line Usage

```bash
python game_engine_gui.py
```

Then interact using the Connect6 protocol:
```
name            # Returns: name ECOJMB
genmove black   # Generate move for black
genmove white   # Generate move for white
play J10        # Play move at J10
quit            # Exit engine
```

