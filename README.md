# tertis
# kinda playable tetris game

import pygame
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
COLUMNS = SCREEN_WIDTH // BLOCK_SIZE
ROWS = SCREEN_HEIGHT // BLOCK_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0)     # Z
]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],                        # I
    [[1, 0, 0], [1, 1, 1]],                # J
    [[0, 0, 1], [1, 1, 1]],                # L
    [[1, 1], [1, 1]],                      # O
    [[0, 1, 1], [1, 1, 0]],                # S
    [[0, 1, 0], [1, 1, 1]],                # T
    [[1, 1, 0], [0, 1, 1]]                 # Z
]

# Helper functions
def draw_ghost_piece(surface, piece, grid):
    ghost = Piece(piece.x, piece.y, piece.shape)
    ghost.rotation = piece.rotation
    while valid_space(ghost, grid):
        ghost.y += 1
    ghost.y -= 1

    for i, row in enumerate(ghost.image()):
        for j, val in enumerate(row):
            if val:
                x = ghost.x + j
                y = ghost.y + i
                if y >= 0:
                    pygame.draw.rect(surface, (150, 150, 150), (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 2)

def rotate(shape):
    return [[shape[y][x] for y in range(len(shape) - 1, -1, -1)] for x in range(len(shape[0]))]


def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def image(self):
        return rotate(self.shape) if self.rotation else self.shape

def valid_space(piece, grid):
    for i, row in enumerate(piece.image()):
        for j, cell in enumerate(row):
            if cell:
                x = piece.x + j
                y = piece.y + i
                if x < 0 or x >= COLUMNS or y >= ROWS or (y >= 0 and grid[y][x] != BLACK):
                    return False
    return True

def clear_rows(grid, locked):
    cleared = 0
    for y in range(ROWS-1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            del_row = y
            for x in range(COLUMNS):
                del locked[(x, del_row)]
            for y2 in range(del_row, 0, -1):
                for x in range(COLUMNS):
                    if (x, y2 - 1) in locked:
                        locked[(x, y2)] = locked.pop((x, y2 - 1))
    return cleared

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(surface, grid[y][x],
                             (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))
    for x in range(COLUMNS):
        pygame.draw.line(surface, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))

def draw_window(surface, grid, score, current_piece):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    draw_ghost_piece(surface, current_piece, grid)
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f"Score: {score}", 1, (255, 255, 255))
    surface.blit(label, (10, 10))
    pygame.display.update()

def get_new_piece():
    return Piece(COLUMNS // 2 - 2, 0, random.choice(SHAPES))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    grid = create_grid()
    locked_positions = {}

    current_piece = get_new_piece()
    next_piece = get_new_piece()
    fall_time = 0
    fall_speed = 0.5
    fast_drop = False
    score = 0
    run = True

    move_sideways_timer = 0
    move_sideways_delay = 100  # milliseconds

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(FPS)
        fall_time += dt
        move_sideways_timer += dt

        keys = pygame.key.get_pressed()
        fast_drop = keys[pygame.K_DOWN]

        # Side movement (hold left/right)
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            if move_sideways_timer > move_sideways_delay:
                move_sideways_timer = 0
                dx = -1 if keys[pygame.K_LEFT] else 1
                current_piece.x += dx
                if not valid_space(current_piece, grid):
                    current_piece.x -= dx
        else:
            move_sideways_timer = move_sideways_delay + 1

        current_speed = 0.05 if fast_drop else fall_speed
        if fall_time / 1000 >= current_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                for i, row in enumerate(current_piece.image()):
                    for j, val in enumerate(row):
                        if val:
                            locked_positions[(current_piece.x + j, current_piece.y + i)] = current_piece.color
                current_piece = next_piece
                next_piece = get_new_piece()
                score += clear_rows(grid, locked_positions) * 100

        # Process events (single key presses)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % 4
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % 4
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    for i, row in enumerate(current_piece.image()):
                        for j, val in enumerate(row):
                            if val:
                                locked_positions[(current_piece.x + j, current_piece.y + i)] = current_piece.color
                    current_piece = next_piece
                    next_piece = get_new_piece()
                    score += clear_rows(grid, locked_positions) * 100

        for i, row in enumerate(current_piece.image()):
            for j, val in enumerate(row):
                if val:
                    x = current_piece.x + j
                    y = current_piece.y + i
                    if y >= 0:
                        grid[y][x] = current_piece.color

        draw_window(screen, grid, score, current_piece)

        # Game Over check
        if any(y < 1 for (x, y) in locked_positions):
            run = False

    pygame.quit()


print("Game starting...")
if __name__ == "__main__":
    main()
