

# This project implements a BDI (Belief-Desire-Intention) agent to solve the Wumpus World challenge.

---

## 📋 Project Structure

```
wumpus-bdi-python/
├── main.py                   # Main entry point
├── wumpus_environment.py     # Environment implementation
├── bdi_agent.py             # BDI Agent implementation
├── simulation.py            # Simulation runner and evaluator
├── visualizer.py            # Visualization module
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

---

##  Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install numpy matplotlib
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```
### Clone Repository

```bash
git clone https://github.com/fortem751/Project-ML/tree/main/Wumpus World
cd Wumpus World
```

---

##  Usage

### Run Single Demonstration (with visualization)

```bash
python main.py --mode demo
```

This will:
- Run a single simulation with full visualization
- Display the BDI reasoning at each step
- Show agent's beliefs, desires, and intentions
- Visualize the grid with agent, pits, wumpus, and gold

### Run Multiple Simulations (for evaluation)

```bash
python main.py --mode eval --num-sims 20
```

This will:
- Run multiple simulations with different configurations
- Test various world sizes and difficulty levels
- Generate statistics (success rate, average steps, etc.)
- Save results to `evaluation_results.txt`

---


## License

This project is created for educational purposes.