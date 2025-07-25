import pygame
import random
import math
import os

# --- Game Constants ---
WIDTH, HEIGHT = 1280, 720
FPS = 60
PLAYER_SPEED = 5
PLAYER_HEALTH_MAX = 100
PLAYER_HEAL_ON_MINIBOSS_KILL = 30
BULLET_SPEED = 7
PLAYER_SHOOT_DELAY = 150
ENEMY_SPEED = 3
GREEN_ENEMY_SPEED = 1.5
MINI_BOSS_SPEED = 1.0
ENEMY_SPAWN_RATE = 45
MINI_BOSS_SPAWN_TIME = 10 * FPS
SCORE_PER_KILL = 10
SCORE_PER_MINI_BOSS_KILL = 50
ENEMY_HEALTH = 1
GREEN_ENEMY_HEALTH = 2
MINI_BOSS_HEALTH = 4
MINI_BOSS_BULLET_SPEED = 6
MINI_BOSS_SHOOT_DELAY = PLAYER_SHOOT_DELAY * 2

# --- New Boss Constants ---
TRIANGLE_BOSS_HEALTH = 50
TRIANGLE_BOSS_SPEED = 0.8
TRIANGLE_BOSS_SIZE = 70
TRIANGLE_BOSS_SCORE = 200
TRIANGLE_BOSS_SPAWN_SCORE_INTERVAL = 1000
TRIANGLE_BOSS_SHOOT_DELAY = MINI_BOSS_SHOOT_DELAY

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREY = (100, 100, 100)

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Shooter")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Load Sounds ---
game_folder = os.path.dirname(__file__)
sound_folder = os.path.join(game_folder, 'sounds')

try:
    gun_sound = pygame.mixer.Sound(os.path.join(sound_folder, 'gunshot.wav'))
    player_death_sound = pygame.mixer.Sound(os.path.join(sound_folder, 'death.mp3'))
    enemy_death_sound = pygame.mixer.Sound(os.path.join(sound_folder, 'hurt.mp3'))
except pygame.error as e:
    print(f"Could not load sound file: {e}")
    gun_sound = None
    player_death_sound = None
    enemy_death_sound = None


# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH_MAX
        self.shoot_delay = PLAYER_SHOOT_DELAY
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if gun_sound:
                gun_sound.play()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_center_x, player_center_y = self.rect.center
            angle = math.atan2(mouse_y - player_center_y, mouse_x - player_center_x)
            bullet = Bullet(player_center_x, player_center_y, angle)
            all_sprites.add(bullet)
            player_bullets.add(bullet)

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
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# --- Enemy Class (Red Circle) ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (12, 12), 12)
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
        else:
            x = WIDTH + 50
            y = random.randint(0, HEIGHT)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ENEMY_SPEED
        self.health = ENEMY_HEALTH

    def update(self):
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
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (20, 20), 20)
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
        else:
            x = WIDTH + 50
            y = random.randint(0, HEIGHT)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = GREEN_ENEMY_SPEED
        self.health = GREEN_ENEMY_HEALTH

    def update(self):
        player_center = player.rect.center
        enemy_center = self.rect.center
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.rect.x += self.speed * (dx / dist)
            self.rect.y += self.speed * (dy / dist)

# --- Bullet Class for Mini-Boss and Triangle Boss ---
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, color):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (7, 7), 7)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = MINI_BOSS_BULLET_SPEED
        self.vel_x = self.speed * math.cos(angle)
        self.vel_y = self.speed * math.sin(angle)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# --- Mini-Boss Class (Purple, Shoots Back) ---
class MiniBoss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PURPLE, (30, 30), 30)
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
        else:
            x = WIDTH + 70
            y = random.randint(0, HEIGHT)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = MINI_BOSS_SPEED
        self.health = MINI_BOSS_HEALTH
        self.shoot_delay = MINI_BOSS_SHOOT_DELAY
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        player_center = player.rect.center
        boss_center = self.rect.center
        dx = player_center[0] - boss_center[0]
        dy = player_center[1] - boss_center[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.rect.x += self.speed * (dx / dist)
            self.rect.y += self.speed * (dy / dist)

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

    def shoot(self):
        player_center_x, player_center_y = player.rect.center
        boss_center_x, boss_center_y = self.rect.center
        angle = math.atan2(player_center_y - boss_center_y, player_center_x - boss_center_x)
        bullet = BossBullet(boss_center_x, boss_center_y, angle, PURPLE)
        all_sprites.add(bullet)
        mini_boss_bullets.add(bullet)

# --- Triangle Boss Class (Yellow, Bigger, Slower, More Health, Stops other spawns, Shoots Back) ---
class TriangleBoss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TRIANGLE_BOSS_SIZE, TRIANGLE_BOSS_SIZE), pygame.SRCALPHA)
        points = [
            (TRIANGLE_BOSS_SIZE // 2, 0),
            (0, TRIANGLE_BOSS_SIZE),
            (TRIANGLE_BOSS_SIZE, TRIANGLE_BOSS_SIZE)
        ]
        pygame.draw.polygon(self.image, YELLOW, points)
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, WIDTH)
            y = -TRIANGLE_BOSS_SIZE
        elif side == 'bottom':
            x = random.randint(0, WIDTH)
            y = HEIGHT + TRIANGLE_BOSS_SIZE
        elif side == 'left':
            x = -TRIANGLE_BOSS_SIZE
            y = random.randint(0, HEIGHT)
        else:
            x = WIDTH + TRIANGLE_BOSS_SIZE
            y = random.randint(0, HEIGHT)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = TRIANGLE_BOSS_SPEED
        self.health = TRIANGLE_BOSS_HEALTH
        self.shoot_delay = TRIANGLE_BOSS_SHOOT_DELAY
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        player_center = player.rect.center
        boss_center = self.rect.center
        dx = player_center[0] - boss_center[0]
        dy = player_center[1] - boss_center[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.rect.x += self.speed * (dx / dist)
            self.rect.y += self.speed * (dy / dist)

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()

    def shoot(self):
        player_center_x, player_center_y = player.rect.center
        boss_center_x, boss_center_y = self.rect.center
        angle = math.atan2(player_center_y - boss_center_y, player_center_x - boss_center_x)
        bullet = BossBullet(boss_center_x, boss_center_y, angle, RED)
        all_sprites.add(bullet)
        mini_boss_bullets.add(bullet)


# --- Health Bar Function ---
def draw_health_bar(surface, x, y, health, max_health, width, height):
    if health < 0:
        health = 0
    fill = (health / max_health) * width
    outline_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

# --- Game Variables ---
score = 0
game_over = False
enemy_spawn_timer = 0
mini_boss_spawn_timer = 0
triangle_boss_active = False
last_triangle_boss_score = 0

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
mini_boss_bullets = pygame.sprite.Group()
triangle_boss_group = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# --- Game Loop ---
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        all_sprites.update()

        if not triangle_boss_active:
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= ENEMY_SPAWN_RATE:
                if random.random() < 0.7:
                    enemy = Enemy()
                else:
                    enemy = EnemyGreen()
                all_sprites.add(enemy)
                enemies.add(enemy)
                enemy_spawn_timer = 0

            mini_boss_spawn_timer += 1
            if mini_boss_spawn_timer >= MINI_BOSS_SPAWN_TIME:
                mini_boss = MiniBoss()
                all_sprites.add(mini_boss)
                enemies.add(mini_boss)
                mini_boss_spawn_timer = 0

        if score >= (last_triangle_boss_score + TRIANGLE_BOSS_SPAWN_SCORE_INTERVAL) and not triangle_boss_active:
            triangle_boss = TriangleBoss()
            all_sprites.add(triangle_boss)
            enemies.add(triangle_boss)
            triangle_boss_group.add(triangle_boss)
            triangle_boss_active = True
            last_triangle_boss_score = (score // TRIANGLE_BOSS_SPAWN_SCORE_INTERVAL) * TRIANGLE_BOSS_SPAWN_SCORE_INTERVAL

        hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
        for enemy_hit, bullet_hit_list in hits.items():
            enemy_hit.health -= len(bullet_hit_list)
            if enemy_hit.health <= 0:
                enemy_hit.kill()
                if enemy_death_sound:
                    enemy_death_sound.play()
                if isinstance(enemy_hit, MiniBoss):
                    score += SCORE_PER_MINI_BOSS_KILL
                    player.health = min(player.health + PLAYER_HEAL_ON_MINIBOSS_KILL, PLAYER_HEALTH_MAX)
                elif isinstance(enemy_hit, TriangleBoss):
                    score += TRIANGLE_BOSS_SCORE
                    triangle_boss_active = False
                else:
                    score += SCORE_PER_KILL

        player_enemy_hits = pygame.sprite.spritecollide(player, enemies, True)
        if player_enemy_hits:
            player.take_damage(len(player_enemy_hits) * 20)

        player_bullet_hits = pygame.sprite.spritecollide(player, mini_boss_bullets, True)
        if player_bullet_hits:
            player.take_damage(len(player_bullet_hits) * 10)

        if player.health <= 0 and not game_over:
            game_over = True
            if player_death_sound:
                player_death_sound.play()


    screen.fill(BLACK)

    all_sprites.draw(screen)

    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    draw_health_bar(screen, 10, 50, player.health, PLAYER_HEALTH_MAX, 200, 20)
    health_text = font.render(f"Health: {player.health}/{PLAYER_HEALTH_MAX}", True, WHITE)
    screen.blit(health_text, (10, 80))


    if game_over:
        game_over_text = font.render("GAME OVER!", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(game_over_text, text_rect)
        screen.blit(restart_text, restart_rect)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            score = 0
            game_over = False
            all_sprites.empty()
            player_bullets.empty()
            enemies.empty()
            mini_boss_bullets.empty()
            triangle_boss_group.empty()
            player = Player()
            all_sprites.add(player)
            enemy_spawn_timer = 0
            mini_boss_spawn_timer = 0
            triangle_boss_active = False
            last_triangle_boss_score = 0

    pygame.display.flip()

pygame.quit()