import pygame
import random
import math

# Game Configuration
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Color Palette
DEEP_BLUE = (0, 32, 64)
LIGHT_BLUE = (64, 164, 223)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 0, 128)

class OceanGame:
    """
    Main game class managing the entire underwater exploration experience
    """
    def __init__(self):
        """Initialize pygame and game systems"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ocean Explorer: Underwater Discovery")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Create game objects
        self.diver = Diver()
        self.ocean = Ocean()
        self.discovery_manager = DiscoveryManager()
        
        # Game state variables
        self.score = 0
        self.depth = 0
        self.game_over = False
        
        # Lighting system
        self.light_radius = 200
        self.light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    def handle_events(self):
        """Handle pygame events and user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Restart game
            if self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset_game()
        
        return True
    
    def update(self):
        """Update game logic each frame"""
        if not self.game_over:
            # Update diver
            self.diver.update()
            
            # Update ocean and its elements
            self.ocean.update()
            
            # Update discoveries
            self.discovery_manager.update(self.diver)
            
            # Check for discoveries
            discovered = self.discovery_manager.check_discoveries(self.diver)
            if discovered:
                self.score += discovered
            
            # Update depth
            self.depth = abs(self.diver.y)
            
            # Check for game over conditions
            if self.diver.oxygen <= 0:
                self.game_over = True
    
    def draw(self):
        """Draw all game elements with dynamic lighting"""
        # Clear the screen with ocean background
        self.screen.fill(DEEP_BLUE)
        
        # Draw ocean elements
        self.ocean.draw(self.screen)
        
        # Draw discoveries
        self.discovery_manager.draw(self.screen)
        
        # Draw diver
        self.diver.draw(self.screen)
        
        # Create lighting effect
        self.create_lighting_effect()
        
        # Draw UI
        self.draw_ui()
        
        # Update display
        pygame.display.flip()
    
    def create_lighting_effect(self):
        """Create a dynamic lighting system for underwater exploration"""
        # Clear previous lighting
        self.light_surface.fill((0, 0, 0, 200))  # Dark overlay
        
        # Create radial gradient light around the diver
        for r in range(self.light_radius, 0, -10):
            alpha = int(255 * (r / self.light_radius) ** 2)
            light_color = (255, 255, 255, alpha)
            pygame.draw.circle(
                self.light_surface, 
                light_color, 
                (int(self.diver.x), int(self.diver.y)), 
                r
            )
        
        # Blend lighting with screen
        self.screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    def draw_ui(self):
        """Draw game user interface"""
        if not self.game_over:
            # Oxygen bar
            oxygen_width = 200
            oxygen_height = 20
            oxygen_percentage = self.diver.oxygen / self.diver.max_oxygen
            pygame.draw.rect(self.screen, WHITE, 
                             (10, 10, oxygen_width, oxygen_height), 2)
            pygame.draw.rect(self.screen, (0, 255, 0), 
                             (10, 10, oxygen_width * oxygen_percentage, oxygen_height))
            
            # Score and depth
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            depth_text = self.font.render(f"Depth: {int(self.depth)}m", True, WHITE)
            self.screen.blit(score_text, (10, 40))
            self.screen.blit(depth_text, (10, 80))
        else:
            # Game over screen
            game_over_text = self.font.render("Game Over!", True, WHITE)
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            self.screen.blit(game_over_text, 
                             (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                              SCREEN_HEIGHT//2 - 50))
            self.screen.blit(restart_text, 
                             (SCREEN_WIDTH//2 - restart_text.get_width()//2, 
                              SCREEN_HEIGHT//2 + 50))
    
    def reset_game(self):
        """Reset the game to its initial state"""
        self.diver = Diver()
        self.ocean = Ocean()
        self.discovery_manager = DiscoveryManager()
        self.score = 0
        self.depth = 0
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

class Diver:
    """Represents the player's diving character"""
    def __init__(self):
        """Initialize diver attributes"""
        self.width = 40
        self.height = 60
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        
        # Movement
        self.speed = 5
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Oxygen system
        self.max_oxygen = 1000
        self.oxygen = self.max_oxygen
        self.oxygen_drain_rate = 1
        
        # Color
        self.color = (0, 200, 255)
    
    def update(self):
        """Update diver movement and oxygen"""
        # Handle input for movement
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
        else:
            self.velocity_x *= 0.9  # Friction
        
        # Vertical movement
        if keys[pygame.K_UP]:
            self.velocity_y = -self.speed
        elif keys[pygame.K_DOWN]:
            self.velocity_y = self.speed
        else:
            self.velocity_y *= 0.9  # Friction
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Keep diver on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        
        # Drain oxygen
        self.oxygen -= self.oxygen_drain_rate
        
        # Slowly restore oxygen when near surface
        if self.y < 100:
            self.oxygen = min(self.max_oxygen, self.oxygen + 2)
    
    def draw(self, screen):
        """Draw the diver"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw simple dive mask
        pygame.draw.circle(screen, WHITE, 
                           (int(self.x + self.width // 2), 
                            int(self.y + self.height // 4)), 
                           10)

class Ocean:
    """Manages ocean environment and background elements"""
    def __init__(self):
        """Initialize ocean characteristics"""
        self.bubbles = []
        self.create_initial_bubbles()
        
        # Create underwater terrain
        self.terrain = self.generate_terrain()
    
    def create_initial_bubbles(self):
        """Generate initial set of bubbles"""
        for _ in range(50):
            self.bubbles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'speed': random.uniform(0.5, 2),
                'size': random.randint(2, 10)
            })
    
    def generate_terrain(self):
        """Generate procedural underwater terrain"""
        terrain = []
        x = 0
        y = SCREEN_HEIGHT * 0.7
        while x < SCREEN_WIDTH:
            terrain.append((x, y))
            # Add some randomness to terrain
            y += random.randint(-20, 20)
            y = max(SCREEN_HEIGHT * 0.6, min(y, SCREEN_HEIGHT * 0.9))
            x += 50
        return terrain
    
    def update(self):
        """Update ocean elements"""
        # Update bubbles
        for bubble in self.bubbles:
            bubble['y'] -= bubble['speed']
            
            # Reset bubble if it goes off screen
            if bubble['y'] < 0:
                bubble['y'] = SCREEN_HEIGHT
                bubble['x'] = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen):
        """Draw ocean elements"""
        # Draw bubbles
        for bubble in self.bubbles:
            pygame.draw.circle(screen, (255, 255, 255, 100), 
                               (int(bubble['x']), int(bubble['y'])), 
                               int(bubble['size']))
        
        # Draw terrain
        if len(self.terrain) > 1:
            pygame.draw.lines(screen, (100, 100, 100), False, self.terrain, 3)

class DiscoveryManager:
    """Manages underwater discoveries and collectibles"""
    def __init__(self):
        """Initialize discoveries"""
        self.discoveries = []
        self.spawn_timer = 0
        self.spawn_interval = 180  # Frames between spawns
    
    def update(self, diver):
        """Update discovery spawning and management"""
        self.spawn_timer += 1
        
        # Spawn new discoveries periodically
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_discovery(diver)
            self.spawn_timer = 0
        
        # Remove collected or out-of-bounds discoveries
        self.discoveries = [
            d for d in self.discoveries 
            if not d.is_collected and d.y < SCREEN_HEIGHT
        ]
    
    def spawn_discovery(self, diver):
        """Spawn a new discovery based on current depth"""
        discovery_types = [
            TreasureChest,
            SeaCreature,
            AncientArtifact
        ]
        
        # Choose discovery type
        discovery_class = random.choice(discovery_types)
        
        # Spawn near, but not too close to the diver
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(100, SCREEN_HEIGHT)
        
        self.discoveries.append(discovery_class(x, y))
    
    def check_discoveries(self, diver):
        """Check for discoveries near the diver"""
        score = 0
        for discovery in self.discoveries:
            if discovery.check_collision(diver):
                score += discovery.value
                discovery.is_collected = True
        return score
    
    def draw(self, screen):
        """Draw all discoveries"""
        for discovery in self.discoveries:
            discovery.draw(screen)

class Discovery:
    """Base class for underwater discoveries"""
    def __init__(self, x, y, size, color, value):
        """Initialize discovery attributes"""
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.value = value
        self.is_collected = False
    
    def check_collision(self, diver):
        """Check if diver is close enough to collect"""
        # Calculate distance between diver and discovery
        distance = math.sqrt(
            (self.x - diver.x)**2 + 
            (self.y - diver.y)**2
        )
        return distance < (self.size + max(diver.width, diver.height))
    
    def draw(self, screen):
        """Draw discovery"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class TreasureChest(Discovery):
    """A treasure chest discovery"""
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            size=20, 
            color=(255, 215, 0),  # Gold color
            value=50
        )

class SeaCreature(Discovery):
    """A unique sea creature discovery"""
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            size=15, 
            color=(0, 255, 255),  # Cyan color
            value=30
        )

class AncientArtifact(Discovery):
    """An ancient underwater artifact"""
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            size=25, 
            color=(128, 0, 128),  # Purple color
            value=100
        )

# Run the game
if __name__ == "__main__":
    game = OceanGame()
    game.run()