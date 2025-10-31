import tkinter as tk
from tkinter import Canvas
import heapq

# --- 1. A* Pathfinding Algorithm (Core AI Logic) ---

def manhattan_distance(start_pos, end_pos):
    """Heuristic function for A*."""
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    return abs(start_x - end_x) + abs(start_y - end_y)

def a_star_search(maze, start, goal):
    """A* search to find the shortest path."""
    if not (0 <= goal[1] < len(maze) and 0 <= goal[0] < len(maze[0]) and maze[goal[1]][goal[0]] != 1):
        return None # Goal is outside bounds or a wall
        
    frontier = [(0, 0, start)] # (f_cost, g_cost, position)
    came_from = {start: None}
    cost_so_far = {start: 0}
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)] # Right, Left, Down, Up (x, y)

    while frontier:
        current_f, current_g, current_pos = heapq.heappop(frontier)
        
        if current_pos == goal:
            path = []
            while current_pos is not None:
                path.append(current_pos)
                current_pos = came_from[current_pos]
            return path[::-1] # Path from start to goal

        for dx, dy in directions:
            next_pos = (current_pos[0] + dx, current_pos[1] + dy)
            next_x, next_y = next_pos
            
            # Boundary and Wall Check: maze[y][x]
            if 0 <= next_y < len(maze) and 0 <= next_x < len(maze[0]) and maze[next_y][next_x] != 1:
                
                new_cost = current_g + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    h_cost = manhattan_distance(next_pos, goal)
                    f_cost = new_cost + h_cost
                    
                    heapq.heappush(frontier, (f_cost, new_cost, next_pos))
                    came_from[next_pos] = current_pos

    return None # No path found

# --- 2. Game Setup and Drawing (Tkinter Interface) ---

class PacManAI_Game(tk.Tk):
    def __init__(self, maze, tile_size=40):
        super().__init__()
        self.title("Pac-Man Ghost AI (A* Demo)")
        
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.tile_size = tile_size
        
        # Ghost (AI Agent) Start Position (x, y)
        self.ghost_pos = (0, 0)
        
        # Target (Pac-Man) Position (x, y) - This is the dynamic target
        self.target_pos = (4, 4) 
        
        self.canvas = Canvas(self, width=self.cols * tile_size, 
                             height=self.rows * tile_size, bg='black')
        self.canvas.pack()
        
        # Bind mouse click to update the Target (Pac-Man's new location)
        self.canvas.bind("<Button-1>", self.update_target_on_click)

        # UI elements
        self.path_line = None
        self.draw_elements()
        self.calculate_and_draw_path()

    def draw_elements(self):
        """Draws the maze, ghost, and target."""
        self.canvas.delete("all")
        
        # Draw Maze
        for y in range(self.rows):
            for x in range(self.cols):
                color = 'blue' if self.maze[y][x] == 1 else 'black'
                x1, y1 = x * self.tile_size, y * self.tile_size
                x2, y2 = x1 + self.tile_size, y1 + self.tile_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

        # Draw Ghost (AI Agent) - Red Square
        self.draw_agent(self.ghost_pos, 'red', 'ghost')
        
        # Draw Target (Pac-Man) - Yellow Circle
        self.draw_agent(self.target_pos, 'yellow', 'target', is_circle=True)

        # Instruction Text
        self.canvas.create_text(
            10, 10, text="Click and it will make it their (25MCI10342)", anchor="nw", fill="white"
        )
        
    def draw_agent(self, pos, color, tag, is_circle=False):
        """Helper to draw the ghost or the target."""
        x, y = pos
        x1 = x * self.tile_size
        y1 = y * self.tile_size
        x2 = x1 + self.tile_size
        y2 = y1 + self.tile_size
        
        if is_circle:
            # Draw a circle for Pac-Man
            self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=color, tags=tag)
        else:
            # Draw a square for the Ghost
            self.canvas.create_rectangle(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=color, tags=tag)

    def update_target_on_click(self, event):
        """Updates the target position based on a mouse click."""
        new_x = event.x // self.tile_size
        new_y = event.y // self.tile_size
        
        if 0 <= new_y < self.rows and 0 <= new_x < self.cols and self.maze[new_y][new_x] != 1:
            self.target_pos = (new_x, new_y)
            self.draw_elements()
            self.calculate_and_draw_path()

    def calculate_and_draw_path(self):
        """Runs A* and visualizes the resulting path."""
        # 1. Run A*
        path = a_star_search(self.maze, self.ghost_pos, self.target_pos)
        
        # 2. Clear old path line
        self.canvas.delete("path_line")
        
        if path:
            # 3. Convert grid coordinates to canvas pixel coordinates
            # Tkinter needs a flat list of (x1, y1, x2, y2, ...)
            pixel_coords = []
            for x, y in path:
                center_x = x * self.tile_size + self.tile_size / 2
                center_y = y * self.tile_size + self.tile_size / 2
                pixel_coords.extend([center_x, center_y])

            # 4. Draw the Path
            self.path_line = self.canvas.create_line(
                pixel_coords, 
                fill='cyan', 
                width=3, 
                tags="path_line"
            )

        # Bonus: Move the Ghost one step along the path (Simulating AI movement)
        if path and len(path) > 1:
            # The next step is the second element in the path list
            next_step = path[1]
            self.ghost_pos = next_step
            self.after(500, self.draw_elements) # Redraw to show new position
            self.after(500, self.calculate_and_draw_path) # Calculate new path (Simulated real-time)

# --- 3. Main Execution ---

if __name__ == "__main__":
    # The Maze (0 = Path, 1 = Wall) - Use (x, y) coordinates for positions
    GAME_MAZE = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    app = PacManAI_Game(GAME_MAZE)
    app.mainloop()