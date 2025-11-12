
# The visualation program displays a grid with agents, pits, wumpus, and gold.

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


class WumpusVisualizer:

    def __init__(self, size=4):
        self.size = size
        self.fig = None
        self.ax = None

    # Visualize current state of the Wumpus world
    def visualize_world(self, environment, agent, step_num=0, save_path=None):

        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=(10, 10))
        else:
            self.ax.clear()

        # Draw grid
        for i in range(self.size + 1):
            self.ax.plot([i, i], [0, self.size], 'k-', linewidth=1)
            self.ax.plot([0, self.size], [i, i], 'k-', linewidth=1)

        # Draw pits
        for pit in environment.pit_positions:
            x, y = pit[1], self.size - 1 - pit[0]
            rect = patches.Rectangle((x, y), 1, 1, linewidth=2,
                                     edgecolor='black', facecolor='gray', alpha=0.7)
            self.ax.add_patch(rect)
            self.ax.text(x + 0.5, y + 0.5, '⚫', fontsize=40,
                         ha='center', va='center')

        # Draw wumpus
        if environment.wumpus_alive:
            x, y = environment.wumpus_pos[1], self.size - \
                1 - environment.wumpus_pos[0]
            rect = patches.Rectangle((x, y), 1, 1, linewidth=2,
                                     edgecolor='red', facecolor='darkred', alpha=0.5)
            self.ax.add_patch(rect)
            self.ax.text(x + 0.5, y + 0.5, '👹', fontsize=40,
                         ha='center', va='center')

        # Draw gold
        for gold in environment.gold_positions:
            x, y = gold[1], self.size - 1 - gold[0]
            self.ax.text(x + 0.5, y + 0.5, '💰', fontsize=40,
                         ha='center', va='center')

        # Draw agent
        agent_x, agent_y = agent.beliefs['current_position']
        x, y = agent_y, self.size - 1 - agent_x
        rect = patches.Rectangle((x, y), 1, 1, linewidth=3,
                                 edgecolor='blue', facecolor='lightblue', alpha=0.6)
        self.ax.add_patch(rect)
        self.ax.text(x + 0.5, y + 0.5, '🤖', fontsize=40,
                     ha='center', va='center')

        # Draw visited cells (lighter background)
        for visited in agent.beliefs['visited_cells']:
            vx, vy = visited[1], self.size - 1 - visited[0]
            rect = patches.Rectangle((vx, vy), 1, 1, linewidth=1,
                                     edgecolor='none', facecolor='lightgreen', alpha=0.2)
            self.ax.add_patch(rect)

        # Draw safe cells known to agent (very light green)
        for safe in agent.beliefs['safe_cells']:
            if safe not in agent.beliefs['visited_cells']:
                sx, sy = safe[1], self.size - 1 - safe[0]
                if 0 <= sx < self.size and 0 <= sy < self.size:
                    rect = patches.Rectangle((sx, sy), 1, 1, linewidth=1,
                                             edgecolor='none', facecolor='green', alpha=0.1)
                    self.ax.add_patch(rect)

        # Draw suspected dangerous cells
        for suspected in agent.beliefs['suspected_pits'].union(agent.beliefs['suspected_wumpus']):
            px, py = suspected[1], self.size - 1 - suspected[0]
            if 0 <= px < self.size and 0 <= py < self.size:
                rect = patches.Rectangle((px, py), 1, 1, linewidth=1,
                                         edgecolor='red', facecolor='red', alpha=0.2)
                self.ax.add_patch(rect)

        # Mark starting position
        rect = patches.Rectangle((0, self.size - 1), 1, 1, linewidth=2,
                                 edgecolor='green', facecolor='none')
        self.ax.add_patch(rect)
        self.ax.text(0.5, self.size - 0.5, '🏠',
                     fontsize=30, ha='center', va='center')

        # Set axis properties
        self.ax.set_xlim(0, self.size)
        self.ax.set_ylim(0, self.size)
        self.ax.set_aspect('equal')
        self.ax.invert_yaxis()

        # Labels
        self.ax.set_xticks(range(self.size + 1))
        self.ax.set_yticks(range(self.size + 1))
        self.ax.set_xticklabels(range(self.size + 1))
        self.ax.set_yticklabels(range(self.size + 1))

        # Title with agent's current state
        intention = agent.get_current_intention() or "None"
        desires = ", ".join(agent.get_current_desires()) or "None"

        title = f'Wumpus World - Step {step_num}\n'
        title += f'Position: {agent.beliefs["current_position"]} | '
        title += f'Gold: {agent.beliefs["gold_collected"]}/{environment.total_gold}\n'
        title += f'Intention: {intention} | Desires: {desires}'

        self.ax.set_title(title, fontsize=14, fontweight='bold')

        # Legend
        legend_elements = [
            patches.Patch(facecolor='lightblue',
                          edgecolor='blue', label='🤖 Agent'),
            patches.Patch(facecolor='darkred',
                          edgecolor='red', label='👹 Wumpus'),
            patches.Patch(facecolor='gray', edgecolor='black', label='⚫ Pit'),
            patches.Patch(facecolor='lightgreen',
                          edgecolor='none', label='✓ Visited'),
            patches.Patch(facecolor='green', edgecolor='none',
                          label='✓ Safe (Known)'),
            patches.Patch(facecolor='red', alpha=0.2,
                          label='⚠️  Suspected Danger'),
        ]
        self.ax.legend(handles=legend_elements,
                       loc='upper left', bbox_to_anchor=(1, 1))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        plt.pause(0.1)

        return self.fig

    def show(self):
        plt.show()

    def close(self):
        if self.fig:
            plt.close(self.fig)
