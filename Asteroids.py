import pygame
import random

# Game Configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FPS = 60

class Game:
    """
    Main game class that manages the game loop, screen, and overall game state.
    This is the central controller of the game.
    """
    def __init__(self):
        """Initialize pygame, create the screen, and set up game objects"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroid Dodger")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Create game objects
        self.player = Player()
        self.asteroid_manager = AsteroidManager()
        
        # Game state variables
        self.score = 0
        self.game_over = False
        
    def handle_events(self):
        """Handle pygame events like quitting and key presses"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Add any additional event handling here
            if event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_r:
                    self.reset_game()
        
        return True
    
    def update(self):
        """Update game logic each frame"""
        if not self.game_over:
            # Update player movement
            self.player.update()
            
            # Update asteroids
            self.asteroid_manager.update()
            
            # Check for collisions
            for asteroid in self.asteroid_manager.asteroids:
                if self.player.check_collision(asteroid):
                    self.game_over = True
            
            # Increment score
            self.score += 1
    
    def draw(self):
        """Draw all game objects"""
        # Clear the screen
        self.screen.fill(BLACK)
        
        if not self.game_over:
            # Draw player
            self.player.draw(self.screen)
            
            # Draw asteroids
            self.asteroid_manager.draw(self.screen)
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
        else:
            # Game over screen
            game_over_text = self.font.render("Game Over!", True, RED)
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        # Update the display
        pygame.display.flip()
    
    def reset_game(self):
        """Reset the game to its initial state"""
        self.player = Player()
        self.asteroid_manager = AsteroidManager()
        self.score = 0
        self.game_over = False
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Control game speed
            self.clock.tick(FPS)
        
        # Quit the game
        pygame.quit()

class Player:
    """
    Player class representing the controllable character.
    Manages player movement, drawing, and collision detection.
    """
    def __init__(self):
        """Initialize player attributes"""
        self.width = 50
        self.height = 50
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = 5
        self.color = WHITE
    
    def update(self):
        """Update player movement based on key presses"""
        keys = pygame.key.get_pressed()
        
        # Move left
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        
        # Move right
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def draw(self, screen):
        """Draw the player on the screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def check_collision(self, asteroid):
        """
        Check if player collides with an asteroid
        Uses simple rectangular collision detection
        """
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        asteroid_rect = pygame.Rect(asteroid.x, asteroid.y, asteroid.width, asteroid.height)
        
        return player_rect.colliderect(asteroid_rect)

class Asteroid:
    """
    Asteroid class representing obstacles the player must dodge.
    Manages asteroid movement and drawing.
    """
    def __init__(self):
        """Initialize asteroid with random properties"""
        self.width = random.randint(30, 70)
        self.height = random.randint(30, 70)
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height  # Start above the screen
        self.speed = random.randint(3, 8)
        self.color = (random.randint(100, 255), 0, 0)  # Varying shades of red
    
    def update(self):
        """Move the asteroid downwards"""
        self.y += self.speed
    
    def draw(self, screen):
        """Draw the asteroid on the screen"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def is_off_screen(self):
        """Check if asteroid has moved off the bottom of the screen"""
        return self.y > SCREEN_HEIGHT

class AsteroidManager:
    """
    Manages a collection of asteroids.
    Handles asteroid creation, updating, and removal.
    """
    def __init__(self):
        """Initialize the asteroid collection"""
        self.asteroids = []
        self.spawn_timer = 0
        self.spawn_interval = 60  # Frames between asteroid spawns
    
    def update(self):
        """
        Update all asteroids:
        - Move existing asteroids
        - Remove off-screen asteroids
        - Spawn new asteroids
        """
        # Update existing asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update()
            
            # Remove asteroids that are off the screen
            if asteroid.is_off_screen():
                self.asteroids.remove(asteroid)
        
        # Spawn new asteroids
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.asteroids.append(Asteroid())
            self.spawn_timer = 0
    
    def draw(self, screen):
        """Draw all asteroids"""
        for asteroid in self.asteroids:
            asteroid.draw(screen)

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()