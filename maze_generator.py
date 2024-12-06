import random
import pygame
from collections import deque
import time

class MazeGenerator:
    def __init__(self, width, height, difficulty='hard'):
        # Ensure odd dimensions for proper maze generation
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.maze = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.difficulty = difficulty
        self.directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # Right, Down, Left, Up
        
        # Difficulty settings affect the number of alternative paths
        self.extra_paths = {
            'easy': 0.08,    # 10% chance of extra paths
            'medium': 0.002,  # 20% chance of extra paths
            'hard': 0.001     # 30% chance of extra paths
        }[difficulty]

    def generate_maze(self):
        # Initialize all cells as walls
        for y in range(self.height):
            for x in range(self.width):
                self.maze[y][x] = 1

        # Start from a random odd position
        start_x = 1
        start_y = 1
        self.maze[start_y][start_x] = 0

        # Generate the maze using depth-first search
        stack = [(start_x, start_y)]
        visited = set([(start_x, start_y)])

        while stack:
            current_x, current_y = stack[-1]
            neighbors = []

            # Check all possible directions
            random.shuffle(self.directions)
            for dx, dy in self.directions:
                next_x, next_y = current_x + dx, current_y + dy
                if (0 < next_x < self.width-1 and 0 < next_y < self.height-1 and 
                    (next_x, next_y) not in visited):
                    neighbors.append((next_x, next_y, dx, dy))

            if neighbors:
                # Choose a random unvisited neighbor
                next_x, next_y, dx, dy = random.choice(neighbors)
                # Remove the wall between current cell and chosen cell
                self.maze[current_y + dy//2][current_x + dx//2] = 0
                self.maze[next_y][next_x] = 0
                stack.append((next_x, next_y))
                visited.add((next_x, next_y))
            else:
                stack.pop()

        # Add some random extra paths based on difficulty
        self._add_extra_paths()

        # Set start and end points
        self._set_start_end()
        self._rotate_maze()  # Rotate the maze
        return self.maze

    def _add_extra_paths(self):
        """Add additional paths based on difficulty level"""
        extra_paths_count = int((self.width * self.height) * self.extra_paths)
        
        for _ in range(extra_paths_count):
            # Choose a random wall
            x = random.randrange(2, self.width-2)
            y = random.randrange(2, self.height-2)
            
            if self.maze[y][x] == 1:  # If it's a wall
                # Check if removing this wall would connect two passages
                passages = 0
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if self.maze[y+dy][x+dx] == 0:
                        passages += 1
                
                # If it connects exactly two passages, remove it
                if passages >= 2:
                    self.maze[y][x] = 0

    def _create_path(self, start, end):
        """Create a path between two points"""
        # Implement path creation logic here
        # For simplicity, we'll just create a straight path
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        steps = max(abs(dx), abs(dy))
        for i in range(steps + 1):
            x = start[0] + dx * i // steps
            y = start[1] + dy * i // steps
            self.maze[y][x] = 0

    def _set_start_end(self):
        """Set start and end points at opposite corners"""
        # Start at top-left
        self.maze[1][1] = 2
        
        # End at bottom-right
        self.maze[self.height-2][self.width-2] = 3
        
        # Ensure there's a path to both points
        self.maze[1][2] = 0
        self.maze[2][1] = 0
        self.maze[self.height-2][self.width-3] = 0
        self.maze[self.height-3][self.width-2] = 0

    def _rotate_maze(self):
        """Rotate the maze 180 degrees"""
        # Reverse the rows and columns
        self.maze = [row[::-1] for row in self.maze[::-1]]

        # Swap start and end points
        self.maze[1][1], self.maze[self.height-2][self.width-2] = \
            self.maze[self.height-2][self.width-2], self.maze[1][1]

class MazeSolver:
    def __init__(self, maze):
        self.maze = maze
        self.height = len(maze)
        self.width = len(maze[0])
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def solve_dfs(self):
        start = self._find_start()
        end = self._find_end()
        visited = set()
        path = []
        
        def dfs(x, y):
            if (x, y) == end:
                return True
            
            visited.add((x, y))
            for dx, dy in self.directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.width and 0 <= new_y < self.height and 
                    self.maze[new_y][new_x] != 1 and (new_x, new_y) not in visited):
                    path.append((new_x, new_y))
                    if dfs(new_x, new_y):
                        return True
                    path.pop()
            return False
        
        path.append(start)
        dfs(*start)
        return path

    def solve_bfs(self):
        start = self._find_start()
        end = self._find_end()
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == end:
                return path
            
            for dx, dy in self.directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.width and 0 <= new_y < self.height and 
                    self.maze[new_y][new_x] != 1 and (new_x, new_y) not in visited):
                    visited.add((new_x, new_y))
                    new_path = path + [(new_x, new_y)]
                    queue.append(((new_x, new_y), new_path))
        return []

    def _find_start(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == 2:
                    return (x, y)
        return (1, 1)

    def _find_end(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == 3:
                    return (x, y)
        return (self.width-2, self.height-2)

class MazeVisualizer:
    def __init__(self, cell_size=10):
        self.cell_size = cell_size
        self.colors = {
            0: (255, 255, 255),  # Path (white)
            1: (0, 0, 0),        # Wall (black)
            2: (0, 255, 0),      # Start (green)
            3: (255, 0, 0),      # End (red)
            4: (0, 0, 255),      # Solution path (blue)
        }
        pygame.init()
        self.font = pygame.font.Font(None, 36)

    def create_button(self, screen, text, position, size, color):
        button = pygame.Rect(position[0], position[1], size[0], size[1])
        pygame.draw.rect(screen, color, button)
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button.center)
        screen.blit(text_surface, text_rect)
        return button

    def show_difficulty_menu(self):
        menu_width, menu_height = 800, 600
        screen = pygame.display.set_mode((menu_width, menu_height))
        pygame.display.set_caption("Select Maze Difficulty")
        
        button_width, button_height = 200, 50
        difficulties = ['easy', 'medium', 'hard']
        buttons = {}
        
        running = True
        while running:
            screen.fill((255, 255, 255))
            
            # Draw title
            title = self.font.render("Select Difficulty", True, (0, 0, 0))
            title_rect = title.get_rect(center=(menu_width//2, 50))
            screen.blit(title, title_rect)
            
            # Create difficulty buttons
            for i, diff in enumerate(difficulties):
                pos_y = 100 + i * (button_height + 20)
                button = self.create_button(
                    screen, 
                    diff.capitalize(), 
                    ((menu_width - button_width)//2, pos_y),
                    (button_width, button_height),
                    (200, 200, 200)
                )
                buttons[diff] = button
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for diff, button in buttons.items():
                        if button.collidepoint(mouse_pos):
                            return diff
        
        return None

    def visualize(self, maze, solution_path=None):
        height, width = len(maze), len(maze[0])
        window_width = width * self.cell_size
        window_height = height * self.cell_size + 60  # Extra space for button
        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Maze Generator and Solver")
        
        show_solution = False
        solution_button = None
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if solution_button and solution_button.collidepoint(event.pos):
                        show_solution = not show_solution
            
            screen.fill((255, 255, 255))
            
            # Draw maze
            for y in range(height):
                for x in range(width):
                    color = self.colors[maze[y][x]]
                    pygame.draw.rect(screen, color, 
                                   (x * self.cell_size, y * self.cell_size, 
                                    self.cell_size, self.cell_size))
            
            # Draw solution path if show_solution is True
            if show_solution and solution_path:
                for i in range(len(solution_path) - 1):
                    x1, y1 = solution_path[i]
                    x2, y2 = solution_path[i + 1]
                    pygame.draw.line(screen, self.colors[4],
                                   (x1 * self.cell_size + self.cell_size // 2,
                                    y1 * self.cell_size + self.cell_size // 2),
                                   (x2 * self.cell_size + self.cell_size // 2,
                                    y2 * self.cell_size + self.cell_size // 2), 2)
            
            # Draw solution button
            button_text = "Hide Solution" if show_solution else "Show Solution"
            solution_button = self.create_button(
                screen,
                button_text,
                (window_width//2 - 100, height * self.cell_size + 10),
                (200, 40),
                (150, 150, 150)
            )
            
            pygame.display.flip()
        
        pygame.quit()

def main():
    # Initialize visualizer first to show menu
    cell_size = 10  # Default cell size
    visualizer = MazeVisualizer(cell_size)
    
    # Show difficulty selection menu
    difficulty = visualizer.show_difficulty_menu()
    if difficulty is None:
        return
    
    # Generate larger maze with selected difficulty
    width, height = 51, 51  # Increased size for more complexity
    generator = MazeGenerator(width, height, difficulty=difficulty)
    maze = generator.generate_maze()
    
    # Solve maze
    solver = MazeSolver(maze)
    solution_path = solver.solve_bfs()
    
    # Adjust cell size based on maze size for better visualization
    cell_size = min(800 // max(width, height), 20)
    visualizer = MazeVisualizer(cell_size)
    visualizer.visualize(maze, solution_path)

if __name__ == "__main__":
    main()
