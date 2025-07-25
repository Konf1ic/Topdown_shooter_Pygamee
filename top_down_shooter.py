import pygame
import random
import math

# --- Game Constants ---
WIDTH, HEIGHT = 1280, 720
FPS = 60
PLAYER_SPEED = 5
PLAYER_HEALTH_MAX = 100 # Maximum player health
BULLET_SPEED = 7
PLAYER_SHOOT_DELAY = 150 # Player frames between shots
ENEMY_SPEED = 3 # Speed for normal red enemies
GREEN_ENEMY_SPEED = 1.5 # Slower speed for green enemies
MINI_BOSS_SPEED = 1.0 # Even slower speed for mini-boss
ENEMY_SPAWN_RATE = 45  # Frames between enemy spawns (lower is faster)
MINI_BOSS_SPAWN_TIME = 10 * FPS # 10 seconds in frames
SCORE_PER_KILL = 10
SCORE_PER_MINI_BOSS_KILL = 50 # Score for mini-boss
ENEMY_HEALTH = 1 # Health for normal red enemies
GREEN_ENEMY_HEALTH = 2 # Double health for green enemies
MINI_BOSS_HEALTH = 4 # Health for mini-boss
MINI_BOSS_BULLET_SPEED = 6
MINI_BOSS_SHOOT_DELAY = PLAYER_SHOOT_DELAY * 2 # Mini-boss frames between shots (slower than player's)

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128) # New purple color for mini-boss
GREY = (100, 100, 100)

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
        self.health = PLAYER_HEALTH_MAX # Player health
        self.shoot_delay = PLAYER_SHOOT_DELAY
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
            player_bullets.add(bullet) # Changed from 'bullets' to 'player_bullets'

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

# --- Bullet Class (Player's Bullet) ---
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

# --- Enemy Class (Red Circle) ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a circular enemy
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (12, 12), 12)
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
        self.health = ENEMY_HEALTH

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

# --- Green Enemy Class (Bigger, Slower, More Health) ---
class EnemyGreen(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a larger green circular enemy
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (20, 20), 20)
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
        self.speed = GREEN_ENEMY_SPEED
        self.health = GREEN_ENEMY_HEALTH

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

# --- Mini-Boss Class (Purple, Shoots Back) ---
class MiniBoss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA) # Larger size
        pygame.draw.circle(self.image, PURPLE, (30, 30), 30) # Purple circle
        # Spawn at a random edge
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, WIDTH)
            y = -70
        elif side == 'bottom':
            x = random.randint(0, WIDTH)
            y = HEIGHT + 70
        elif side == 'left':
            x = -70
            y = random.randint(0, HEIGHT)
        else: # right
            x = WIDTH + 70
            y = random.randint(0, HEIGHT)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = MINI_BOSS_SPEED
        self.health = MINI_BOSS_HEALTH
        self.shoot_delay = MINI_BOSS_SHOOT_DELAY
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # Move towards the player
        player_center = player.rect.center
        boss_center = self.rect.center
        dx = player_center[0] - boss_center[0]
        dy = player_center[1] - boss_center[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.rect.x += self.speed * (dx / dist)
            self.rect.y += self.speed * (dy / dist)

        # Mini-boss shooting logic
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

    def shoot(self):
        # Calculate bullet direction towards player
        player_center_x, player_center_y = player.rect.center
        boss_center_x, boss_center_y = self.rect.center
        angle = math.atan2(player_center_y - boss_center_y, player_center_x - boss_center_x)
        bullet = MiniBossBullet(boss_center_x, boss_center_y, angle)
        all_sprites.add(bullet)
        mini_boss_bullets.add(bullet)

# --- Mini-Boss Bullet Class ---
class MiniBossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA) # Slightly larger bullet
        pygame.draw.circle(self.image, PURPLE, (7, 7), 7) # Purple bullet
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = MINI_BOSS_BULLET_SPEED
        self.vel_x = self.speed * math.cos(angle)
        self.vel_y = self.speed * math.sin(angle)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        # Remove bullet if it goes off screen
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# --- Health Bar Function ---
def draw_health_bar(surface, x, y, health, max_health, width, height):
    if health < 0:
        health = 0
    fill = (health / max_health) * width
    outline_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2) # Outline

# --- Game Variables ---
score = 0
game_over = False
enemy_spawn_timer = 0
mini_boss_spawn_timer = 0

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
player_bullets = pygame.sprite.Group() # Renamed from 'bullets'
enemies = pygame.sprite.Group() # Contains red, green, and mini-boss enemies
mini_boss_bullets = pygame.sprite.Group() # New group for mini-boss bullets

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

        # Spawn regular enemies (red and green)
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= ENEMY_SPAWN_RATE:
            # Randomly choose which regular enemy to spawn (70% red, 30% green)
            if random.random() < 0.7:
                enemy = Enemy()
            else:
                enemy = EnemyGreen()
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = 0

        # Spawn mini-boss
        mini_boss_spawn_timer += 1
        if mini_boss_spawn_timer >= MINI_BOSS_SPAWN_TIME:
            mini_boss = MiniBoss()
            all_sprites.add(mini_boss)
            enemies.add(mini_boss) # Add mini-boss to general enemies group for player bullet collision
            mini_boss_spawn_timer = 0

        # Collision detection: Player Bullets vs. Enemies (including mini-boss)
        # The first 'False' means enemies are not automatically removed on hit
        hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
        for enemy_hit, bullet_hit_list in hits.items():
            # Decrease health for each bullet that hit the enemy
            enemy_hit.health -= len(bullet_hit_list)
            if enemy_hit.health <= 0:
                enemy_hit.kill() # Remove enemy if health is 0 or less
                if isinstance(enemy_hit, MiniBoss): # Check if it's a mini-boss
                    score += SCORE_PER_MINI_BOSS_KILL
                else:
                    score += SCORE_PER_KILL # Add score only when enemy is truly killed

        # Collision detection: Player vs. Enemies (red, green, mini-boss)
        player_enemy_hits = pygame.sprite.spritecollide(player, enemies, True) # True means enemy is removed on contact
        if player_enemy_hits:
            player.take_damage(len(player_enemy_hits) * 20) # Player takes damage for each enemy hit

        # Collision detection: Player vs. Mini-Boss Bullets
        player_bullet_hits = pygame.sprite.spritecollide(player, mini_boss_bullets, True) # True means bullet is removed
        if player_bullet_hits:
            player.take_damage(len(player_bullet_hits) * 10) # Player takes damage for each mini-boss bullet hit

        # Check if player health is zero
        if player.health <= 0:
            game_over = True

    # --- Drawing ---
    screen.fill(BLACK) # Clear screen

    all_sprites.draw(screen) # Draw all sprites

    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Draw player health bar
    draw_health_bar(screen, 10, 50, player.health, PLAYER_HEALTH_MAX, 200, 20)
    health_text = font.render(f"Health: {player.health}/{PLAYER_HEALTH_MAX}", True, WHITE)
    screen.blit(health_text, (10, 80))


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
            player_bullets.empty()
            enemies.empty()
            mini_boss_bullets.empty()
            player = Player()
            all_sprites.add(player)
            enemy_spawn_timer = 0
            mini_boss_spawn_timer = 0

    # --- Update Display ---
    pygame.display.flip()

pygame.quit()