import pygame
import random
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.radius = 20
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.damage = 10
        self.fire_rate = 500  # milliseconds between shots
        self.last_shot = 0
        self.upgrades = {
            'health': 0,
            'damage': 0,
            'speed': 0,
            'fire_rate': 0
        }
        self.total_coins = 0
        self.coins = 0

    def move(self, keys):
        if keys[pygame.K_a or pygame.K_LEFT] and self.x > self.radius:
            self.x -= self.speed
        if keys[pygame.K_d or pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.radius:
            self.x += self.speed
        if keys[pygame.K_w or pygame.K_UP] and self.y > self.radius:
            self.y -= self.speed
        if keys[pygame.K_s or pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.radius:
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        # Health bar
        health_width = 50
        health_height = 5
        health_x = self.x - health_width // 2
        health_y = self.y - self.radius - 10
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width * (self.health / self.max_health), health_height))

class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=10):
        self.x = x
        self.y = y
        angle = math.atan2(target_y - y, target_x - x)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.radius = 5

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, (0,255,211), (int(self.x), int(self.y)), self.radius)

    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)

class Enemy:
    def __init__(self, player, enemies):
        # Spawn point selection
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = -50
        elif side == 1:  # Right
            self.x = SCREEN_WIDTH + 50
            self.y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Bottom
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT + 50
        else:  # Left
            self.x = -50
            self.y = random.randint(0, SCREEN_HEIGHT)

        self.health = 30
        self.speed = 2
        self.damage = 10
        self.radius = 15
        self.player = player
        
        # Ensure no initial overlap with other enemies
        while any(math.sqrt((self.x - e.x)**2 + (self.y - e.y)**2) < self.radius * 2 for e in enemies):
            side = random.randint(0, 3)
            if side == 0:
                self.x = random.randint(0, SCREEN_WIDTH)
                self.y = -50
            elif side == 1:
                self.x = SCREEN_WIDTH + 50
                self.y = random.randint(0, SCREEN_HEIGHT)
            elif side == 2:
                self.x = random.randint(0, SCREEN_WIDTH)
                self.y = SCREEN_HEIGHT + 50
            else:
                self.x = -50
                self.y = random.randint(0, SCREEN_HEIGHT)

    def move(self, enemies):
        # Update target to current player position
        self.target_x = self.player.x
        self.target_y = self.player.y
        
        # Recalculate angle and movement
        angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed
        
        # Proposed new position
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check collision with other enemies
        collision = False
        for enemy in enemies:
            if enemy != self:
                distance = math.sqrt((new_x - enemy.x)**2 + (new_y - enemy.y)**2)
                if distance < self.radius * 2:
                    collision = True
                    break
        
        # Move if no collision
        if not collision:
            self.x = new_x
            self.y = new_y

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

class Shop:
    def __init__(self, player):
        self.player = player
        self.upgrades = {
            'Health Upgrade': {'cost': 50, 'stat': 'health', 'increase': 10},
            'Damage Upgrade': {'cost': 50, 'stat': 'damage', 'increase': 2},
            'Speed Upgrade': {'cost': 50, 'stat': 'speed', 'increase': 1},
            'Fire Rate Upgrade': {'cost': 50, 'stat': 'fire_rate', 'increase': -100}
        }

    def draw(self, screen):
        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        title = font.render("SHOP", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        coins_text = font.render(f"Total Coins: {self.player.total_coins}", True, WHITE)
        screen.blit(coins_text, (50, 100))

        for i, (name, upgrade) in enumerate(self.upgrades.items()):
            text = font.render(
                f"{name} (Cost: {upgrade['cost']}) - Current Level: {self.player.upgrades[upgrade['stat']]}",
                True, WHITE
            )
            screen.blit(text, (50, 200 + i * 50))

        instruction_text = font.render("Press number keys (1-4) to upgrade, SPACE to continue", True, WHITE)
        screen.blit(instruction_text, (50, SCREEN_HEIGHT - 100))

    def handle_purchase(self, upgrade_name):
        upgrade = self.upgrades[upgrade_name]
        if self.player.total_coins >= upgrade['cost']:
            self.player.total_coins -= upgrade['cost']
            stat = upgrade['stat']
            self.player.upgrades[stat] += 1
            
            if stat == 'health':
                self.player.max_health += upgrade['increase']
                self.player.health = min(self.player.health + upgrade['increase'], self.player.max_health)
            elif stat == 'damage':
                self.player.damage += upgrade['increase']
            elif stat == 'speed':
                self.player.speed += upgrade['increase']
            elif stat == 'fire_rate':
                self.player.fire_rate = max(100, self.player.fire_rate + upgrade['increase'])

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Shooter")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.running = True
        self.wave = 1
        self.enemy_count = 0
        self.max_enemies = 5
        self.font = pygame.font.Font(None, 36)
        self.game_continues = True

    def spawn_enemies(self):
        while len(self.enemies) < self.max_enemies:
            new_enemy = Enemy(self.player, self.enemies)
            self.enemies.append(new_enemy)
            self.enemy_count += 1

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
        
        # Continuous aiming and shooting
        current_time = pygame.time.get_ticks()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        if current_time - self.player.last_shot > self.player.fire_rate:
            self.bullets.append(Bullet(self.player.x, self.player.y, mouse_x, mouse_y))
            self.player.last_shot = current_time

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)

        # Move bullets
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        # Move and check enemy interactions
        for enemy in self.enemies[:]:
            enemy.move(self.enemies)

            # Check bullet collisions
            for bullet in self.bullets[:]:
                distance = math.sqrt((enemy.x - bullet.x)**2 + (enemy.y - bullet.y)**2)
                if distance < enemy.radius + bullet.radius:
                    enemy.health -= self.player.damage
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)

            # Check enemy-player collision
            player_distance = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
            if player_distance < enemy.radius + self.player.radius:
                self.player.health -= enemy.damage

            # Remove dead enemies
            if enemy.health <= 0:
                
                self.enemies.remove(enemy)
                self.player.coins += 10
                self.player.total_coins += 10
                self.enemy_count -= 1

        # Check wave completion and player health
        if not self.enemies:
            self.enter_shop()
            self.wave += 1
            self.max_enemies += 2
            self.spawn_enemies()

        # Check game over
        if self.player.health <= 0:
            self.game_over()

    def enter_shop(self):
        # Reset current wave coins and enter shop
        self.player.coins = 0
        shop = Shop(self.player)
        shop_active = True
        while shop_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shop_active = False
                    self.running = False
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        shop.handle_purchase('Health Upgrade')
                    elif event.key == pygame.K_2:
                        shop.handle_purchase('Damage Upgrade')
                    elif event.key == pygame.K_3:
                        shop.handle_purchase('Speed Upgrade')
                    elif event.key == pygame.K_4:
                        shop.handle_purchase('Fire Rate Upgrade')
                    elif event.key == pygame.K_SPACE:
                        shop_active = False
            
            shop.draw(self.screen)
            pygame.display.flip()

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw game info
        wave_text = self.font.render(f"Wave: {self.wave}", True, WHITE)
        enemy_text = self.font.render(f"Enemies: {self.enemy_count}", True, WHITE)
        coins_text = self.font.render(f"Wave Coins: {self.player.coins}", True, WHITE)
        total_coins_text = self.font.render(f"Total Coins: {self.player.total_coins}", True, WHITE)
        
        self.screen.blit(wave_text, (10, 10))
        self.screen.blit(enemy_text, (10, 50))
        self.screen.blit(coins_text, (10, 90))
        self.screen.blit(total_coins_text, (10, 130))

        pygame.display.flip()

    def game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.font.render("GAME OVER", True, RED)
        wave_text = self.font.render(f"Waves Survived: {self.wave}", True, WHITE)
        coins_text = self.font.render(f"Total Coins Earned: {self.player.total_coins}", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
        pygame.time.wait(3000)
        self.running = False

    def run(self):
        # First wave preparation
        self.spawn_enemies()
        self.enter_shop()
        
        # Main game loop
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()