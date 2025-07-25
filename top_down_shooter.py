import pygame
import random
import math

# --- Game Constants ---
WIDTH, HEIGHT = 1280, 720 # Increased screen size
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 5 # Bullet speed set to 5
ENEMY_SPEED = 3 # Increased enemy speed
ENEMY_SPAWN_RATE = 60  # Frames between enemy spawns (lower is faster)
SCORE_PER_KILL = 10

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Shooter")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36) # Default font, size 36

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = PLAYER_SPEED
        self.health = 100
        self.shoot_delay = 150
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # Get keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        # Shooting with mouse click held down
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]: # Check if left mouse button is held down
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            # Calculate bullet direction towards mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_center_x, player_center_y = self.rect.center
            angle = math.atan2(mouse_y - player_center_y, mouse_x - player_center_x)
            bullet = Bullet(player_center_x, player_center_y, angle)
            all_sprites.add(bullet)
            bullets.add(bullet)

# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED
        self.vel_x = self.speed * math.cos(angle)
        self.vel_y = self.speed * math.sin(angle)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        # Remove bullet if it goes off screen
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a circular enemy instead of a square
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA) # SRCALPHA for transparency
        pygame.draw.circle(self.image, RED, (12, 12), 12) # Draw a red circle with radius 12, centered at (12,12)
        # Spawn enemy at a random edge of the screen
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, WIDTH)
            y = -50
        elif side == 'bottom':
            x = random.randint(0, WIDTH)
            y = HEIGHT + 50
        elif side == 'left':
            x = -50
            y = random.randint(0, HEIGHT)
        else: # right
            x = WIDTH + 50
            y = random.randint(0, HEIGHT)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ENEMY_SPEED

    def update(self):
        # Move towards the player
        player_center = player.rect.center
        enemy_center = self.rect.center
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.rect.x += self.speed * (dx / dist)
            self.rect.y += self.speed * (dy / dist)

# --- Game Variables ---
score = 0
game_over = False
enemy_spawn_timer = 0

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# --- Game Loop ---
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(FPS)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # --- Update ---
        all_sprites.update()

        # Spawn enemies
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= ENEMY_SPAWN_RATE:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = 0

        # Collision detection: Bullets vs. Enemies
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += SCORE_PER_KILL

        # Collision detection: Player vs. Enemies
        player_hits = pygame.sprite.spritecollide(player, enemies, False) # False means enemy is not removed
        if player_hits:
            # For simplicity, if player hits any enemy, it's game over
            # In a real game, player would take damage and enemies might be removed
            game_over = True

    # --- Drawing ---
    screen.fill(BLACK) # Clear screen

    all_sprites.draw(screen) # Draw all sprites

    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Display Game Over message
    if game_over:
        game_over_text = font.render("GAME OVER!", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(game_over_text, text_rect)
        screen.blit(restart_text, restart_rect)

        # Check for restart
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reset game
            score = 0
            game_over = False
            all_sprites.empty()
            bullets.empty()
            enemies.empty()
            player = Player()
            all_sprites.add(player)
            enemy_spawn_timer = 0

    # --- Update Display ---
    pygame.display.flip()

pygame.quit()