import pygame
import sys
import random
import heapq
from enum import Enum
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 8
CELL_SIZE = 60
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + 200
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + 100
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GREEN = (0, 128, 0)

class GameState(Enum):
    MENU = 1
    PLAYER_HIDING = 2
    COMPUTER_SEEKING = 3
    COMPUTER_HIDING = 4
    PLAYER_SEEKING = 5
    GAME_OVER = 6

class HideSeekGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Hide & Seek with A* Pathfinding")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.hiding_spots = []
        self.generate_hiding_spots()
        
        self.state = GameState.MENU
        self.max_steps = 15
        self.steps_remaining = self.max_steps
        self.hidden_position = None
        self.seeker_position = (0, 0)
        self.last_distance = float('inf')
        self.feedback_text = ""
        self.winner = None
        
    def generate_hiding_spots(self):
        """Generate random hiding spots on the grid"""
        self.hiding_spots = []
        num_spots = random.randint(8, 12)
        
        for _ in range(num_spots):
            while True:
                x = random.randint(0, GRID_SIZE - 1)
                y = random.randint(0, GRID_SIZE - 1)
                if (x, y) not in self.hiding_spots:
                    self.hiding_spots.append((x, y))
                    break
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def a_star_distance(self, start: Tuple[int, int], goal: Tuple[int, int]) -> int:
        """Calculate shortest path distance using A* algorithm"""
        if start == goal:
            return 0
            
        open_set = [(0, start)]
        g_score = {start: 0}
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
            
            if current == goal:
                return g_score[current]
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if (0 <= neighbor[0] < GRID_SIZE and 
                    0 <= neighbor[1] < GRID_SIZE):
                    
                    tentative_g = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + self.manhattan_distance(neighbor, goal)
                        heapq.heappush(open_set, (f_score, neighbor))
        
        return float('inf')  # No path found
    
    def get_temperature_feedback(self, distance: int) -> Tuple[str, tuple]:
        """Get hot/cold feedback based on distance"""
        if distance == 0:
            return "FOUND!", GREEN
        elif distance <= 2:
            return "BURNING HOT!", RED
        elif distance <= 4:
            return "Hot", ORANGE
        elif distance <= 6:
            return "Warm", YELLOW
        elif distance <= 10:
            return "Cool", LIGHT_GRAY
        else:
            return "Cold", BLUE
    
    def computer_seek(self):
        """Computer's turn to seek the player"""
        if self.steps_remaining <= 0:
            self.winner = "Player"
            self.state = GameState.GAME_OVER
            return
        
        # Simple AI: move towards the closest hiding spot
        best_move = None
        best_distance = float('inf')
        
        current_x, current_y = self.seeker_position
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = current_x + dx, current_y + dy
            
            if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                min_dist_to_hiding_spot = min(
                    self.a_star_distance((new_x, new_y), spot) 
                    for spot in self.hiding_spots
                )
                
                if min_dist_to_hiding_spot < best_distance:
                    best_distance = min_dist_to_hiding_spot
                    best_move = (new_x, new_y)
        
        if best_move:
            self.seeker_position = best_move
            self.steps_remaining -= 1
            
            # Check if computer found the player
            if self.seeker_position == self.hidden_position:
                self.winner = "Computer"
                self.state = GameState.GAME_OVER
            else:
                distance = self.a_star_distance(self.seeker_position, self.hidden_position)
                self.feedback_text, _ = self.get_temperature_feedback(distance)
    
    def handle_click(self, pos):
        """Handle mouse clicks"""
        x, y = pos
        grid_x = x // CELL_SIZE
        grid_y = y // CELL_SIZE
        
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            if self.state == GameState.PLAYER_HIDING:
                if (grid_x, grid_y) in self.hiding_spots:
                    self.hidden_position = (grid_x, grid_y)
                    self.seeker_position = (0, 0)
                    self.steps_remaining = self.max_steps
                    self.state = GameState.COMPUTER_SEEKING
                    self.feedback_text = "Computer is seeking..."
            
            elif self.state == GameState.PLAYER_SEEKING:
                if self.steps_remaining > 0:
                    self.seeker_position = (grid_x, grid_y)
                    self.steps_remaining -= 1
                    
                    if self.seeker_position == self.hidden_position:
                        self.winner = "Player"
                        self.state = GameState.GAME_OVER
                    else:
                        distance = self.a_star_distance(self.seeker_position, self.hidden_position)
                        self.feedback_text, _ = self.get_temperature_feedback(distance)
                        
                        if self.steps_remaining == 0:
                            self.winner = "Computer"
                            self.state = GameState.GAME_OVER
    
    def start_new_game(self):
        """Start a new game"""
        self.generate_hiding_spots()
        self.steps_remaining = self.max_steps
        self.hidden_position = None
        self.seeker_position = (0, 0)
        self.feedback_text = ""
        self.winner = None
        
        # Randomly choose who hides first
        if random.choice([True, False]):
            self.state = GameState.PLAYER_HIDING
        else:
            self.state = GameState.COMPUTER_HIDING
            # Computer chooses a random hiding spot
            self.hidden_position = random.choice(self.hiding_spots)
            self.state = GameState.PLAYER_SEEKING
            self.feedback_text = "Find the computer!"
    
    def draw_grid(self):
        """Draw the game grid"""
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                # Color cells based on their type
                if (x, y) in self.hiding_spots:
                    pygame.draw.rect(self.screen, DARK_GREEN, rect)
                else:
                    pygame.draw.rect(self.screen, WHITE, rect)
                
                # Draw seeker position
                if (x, y) == self.seeker_position:
                    pygame.draw.circle(self.screen, RED, rect.center, CELL_SIZE // 3)
                
                # Draw hidden position if game is over
                if (self.state == GameState.GAME_OVER and 
                    (x, y) == self.hidden_position):
                    pygame.draw.circle(self.screen, BLUE, rect.center, CELL_SIZE // 4)
                
                pygame.draw.rect(self.screen, BLACK, rect, 2)
    
    def draw_ui(self):
        """Draw the user interface"""
        ui_x = GRID_SIZE * CELL_SIZE + 10
        
        # Game state
        if self.state == GameState.MENU:
            text = self.big_font.render("Hide & Seek", True, BLACK)
            self.screen.blit(text, (ui_x, 50))
            text = self.font.render("Click to start!", True, BLACK)
            self.screen.blit(text, (ui_x, 100))
        
        elif self.state == GameState.PLAYER_HIDING:
            text = self.font.render("Click on a green", True, BLACK)
            self.screen.blit(text, (ui_x, 50))
            text = self.font.render("hiding spot!", True, BLACK)
            self.screen.blit(text, (ui_x, 70))
        
        elif self.state in [GameState.COMPUTER_SEEKING, GameState.PLAYER_SEEKING]:
            text = self.font.render(f"Steps: {self.steps_remaining}", True, BLACK)
            self.screen.blit(text, (ui_x, 50))
            
            if self.feedback_text:
                text = self.font.render(self.feedback_text, True, BLACK)
                self.screen.blit(text, (ui_x, 80))
        
        elif self.state == GameState.GAME_OVER:
            text = self.big_font.render(f"{self.winner} Wins!", True, BLACK)
            self.screen.blit(text, (ui_x, 50))
            text = self.font.render("Click to play again", True, BLACK)
            self.screen.blit(text, (ui_x, 100))
        
        # Legend
        legend_y = 200
        text = self.font.render("Legend:", True, BLACK)
        self.screen.blit(text, (ui_x, legend_y))
        
        pygame.draw.rect(self.screen, DARK_GREEN, (ui_x, legend_y + 25, 20, 20))
        text = self.font.render("Hiding spots", True, BLACK)
        self.screen.blit(text, (ui_x + 25, legend_y + 25))
        
        pygame.draw.circle(self.screen, RED, (ui_x + 10, legend_y + 60), 8)
        text = self.font.render("Seeker", True, BLACK)
        self.screen.blit(text, (ui_x + 25, legend_y + 50))
        
        pygame.draw.circle(self.screen, BLUE, (ui_x + 10, legend_y + 85), 6)
        text = self.font.render("Hidden player", True, BLACK)
        self.screen.blit(text, (ui_x + 25, legend_y + 75))
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == GameState.MENU:
                        self.start_new_game()
                    elif self.state == GameState.GAME_OVER:
                        self.start_new_game()
                    else:
                        self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == GameState.COMPUTER_SEEKING:
                        self.computer_seek()
            
            # Auto-advance computer seeking
            if self.state == GameState.COMPUTER_SEEKING:
                pygame.time.wait(1000)  # Wait 1 second
                self.computer_seek()
            
            # Draw everything
            self.screen.fill(LIGHT_GRAY)
            
            if self.state != GameState.MENU:
                self.draw_grid()
            
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = HideSeekGame()
    game.run()