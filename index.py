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
                    pygame.draw.rect(surface, (150, 150, 150),
                                     (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 2)

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
        rotated_shape = self.shape
        for _ in range(self.rotation % 4):
            rotated_shape = rotate(rotated_shape)
        return rotated_shape

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
    for y in range(ROWS - 1, -1, -1):
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

# --- Start Screen ---
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def button(surface, text, x, y, width, height, hover_color, default_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(surface, hover_color, (x, y, width, height), border_radius=10)
        if click:
            return True
    else:
        pygame.draw.rect(surface, default_color, (x, y, width, height), border_radius=10)
    draw_text(text, pygame.font.SysFont("comicsans", 30), BLACK, surface, x + width // 2, y + height // 2)
    return False

def start_screen():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 60, bold=True)
    running = True

    while running:
        screen.fill(BLACK)
        draw_text("T", font, (246, 23, 23), screen, SCREEN_WIDTH // 5, 150)
        draw_text('E', font, (210,58,220), screen, SCREEN_WIDTH // 3, 150)
        draw_text('T', font, (96,58,220), screen, SCREEN_WIDTH // 2.15, 150)
        draw_text('R', font, (58,199,220), screen, SCREEN_WIDTH // 1.65, 150)
        draw_text('I', font, (58,220,101), screen, SCREEN_WIDTH // 1.40, 150)
        draw_text('S', font, (220,215,58), screen, SCREEN_WIDTH // 1.20, 150)



        start = button(screen, "Start Game", 60, 300, 170, 50,  (0,255,0),(0,128,255))
        quit_game = button(screen, "Quit", 75, 400, 150, 50, (255, 0, 0), (255, 128, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if start:
            return  # go to main game
        if quit_game:
            pygame.quit()
            exit()

        pygame.display.flip()
        clock.tick(60)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
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

    lock_delay_timer = 0
    lock_delay_limit = 500  # milliseconds
    piece_landed = False

    while run:
        dt = clock.tick(FPS)
        fall_time += dt
        grid = create_grid(locked_positions)
        keys = pygame.key.get_pressed()
        fast_drop = keys[pygame.K_DOWN]

        # Input handling
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
                    current_piece.rotation = (current_piece.rotation - 1) % 4  # Counterclockwise
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation + 1) % 4
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
                    lock_delay_timer = 0
                    piece_landed = False

        # Automatic fall
        current_speed = 0.05 if fast_drop else fall_speed
        if fall_time / 1000 >= current_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                piece_landed = True
            else:
                piece_landed = False
                lock_delay_timer = 0

        # Lock delay
        if piece_landed:
            lock_delay_timer += dt
            if lock_delay_timer >= lock_delay_limit:
                for i, row in enumerate(current_piece.image()):
                    for j, val in enumerate(row):
                        if val:
                            locked_positions[(current_piece.x + j, current_piece.y + i)] = current_piece.color
                current_piece = next_piece
                next_piece = get_new_piece()
                score += clear_rows(grid, locked_positions) * 100
                lock_delay_timer = 0
                piece_landed = False

        # Draw piece on grid
        for i, row in enumerate(current_piece.image()):
            for j, val in enumerate(row):
                if val:
                    x = current_piece.x + j
                    y = current_piece.y + i
                    if y >= 0:
                        grid[y][x] = current_piece.color

        draw_window(screen, grid, score, current_piece)

        # Game Over
        if any(y < 1 for (x, y) in locked_positions):
            run = False

    pygame.quit()


print("Game starting...")
if __name__ == "__main__":
    start_screen()
    main()
