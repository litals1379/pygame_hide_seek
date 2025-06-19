import pygame
import random

# אתחול pygame
pygame.init()

# קבועים
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
CELL_SIZE = WIDTH // COLS

# צבעים
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

# יצירת חלון
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hide and Seek Game")

# מיקום השחקנים
player1_pos = [0, 0]  # כחול
player2_pos = [7, 7]  # אדום

# מיקום המתחבא (ירוק)
def generate_hider_pos():
    while True:
        pos = [random.randint(0, ROWS-1), random.randint(0, COLS-1)]
        if pos != player1_pos and pos != player2_pos:
            return pos

hider_pos = generate_hider_pos()

# משתנים
player1_turn = True
barriers = []
player1_used_action = False
player2_used_action = False

def draw_board():
    screen.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

    # מחסומים
    for pos in barriers:
        rect = pygame.Rect(pos[1]*CELL_SIZE, pos[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GRAY, rect)

    # שחקנים
    pygame.draw.circle(screen, BLUE,
                       (player1_pos[1]*CELL_SIZE + CELL_SIZE//2,
                        player1_pos[0]*CELL_SIZE + CELL_SIZE//2),
                       CELL_SIZE//3)

    pygame.draw.circle(screen, RED,
                       (player2_pos[1]*CELL_SIZE + CELL_SIZE//2,
                        player2_pos[0]*CELL_SIZE + CELL_SIZE//2),
                       CELL_SIZE//3)

    # המתחבא
    pygame.draw.circle(screen, GREEN,
                       (hider_pos[1]*CELL_SIZE + CELL_SIZE//2,
                        hider_pos[0]*CELL_SIZE + CELL_SIZE//2),
                       CELL_SIZE//4)

running = True
winner = None

while running:
    draw_board()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # שחקן 1
        elif event.type == pygame.KEYDOWN and player1_turn:
            old_pos = player1_pos.copy()
            if event.key == pygame.K_UP and player1_pos[0] > 0:
                player1_pos[0] -= 1
            elif event.key == pygame.K_DOWN and player1_pos[0] < ROWS - 1:
                player1_pos[0] += 1
            elif event.key == pygame.K_LEFT and player1_pos[1] > 0:
                player1_pos[1] -= 1
            elif event.key == pygame.K_RIGHT and player1_pos[1] < COLS - 1:
                player1_pos[1] += 1
            elif event.key == pygame.K_SPACE and not player1_used_action:
                r, c = player1_pos
                if c < COLS - 1:
                    barriers.append([r, c])
                    barriers.append([r, c + 1])
                    player1_used_action = True
                    player1_turn = False
                    continue

            if player1_pos in barriers:
                player1_pos = old_pos
            else:
                player1_turn = False

        # שחקן 2
        elif event.type == pygame.KEYDOWN and not player1_turn:
            old_pos = player2_pos.copy()
            if event.key == pygame.K_w and player2_pos[0] > 0:
                player2_pos[0] -= 1
            elif event.key == pygame.K_s and player2_pos[0] < ROWS - 1:
                player2_pos[0] += 1
            elif event.key == pygame.K_a and player2_pos[1] > 0:
                player2_pos[1] -= 1
            elif event.key == pygame.K_d and player2_pos[1] < COLS - 1:
                player2_pos[1] += 1
            elif event.key == pygame.K_SPACE and not player2_used_action:
                r, c = player2_pos
                if c < COLS - 1:
                    barriers.append([r, c])
                    barriers.append([r, c + 1])
                    player2_used_action = True
                    player1_turn = True
                    continue

            if player2_pos in barriers:
                player2_pos = old_pos
            else:
                player1_turn = True

    if player1_pos == hider_pos:
        print("Player 1 found the hider!")
        winner = "Player 1"
        running = False
    elif player2_pos == hider_pos:
        print("Player 2 found the hider!")
        winner = "Player 2"
        running = False

pygame.quit()