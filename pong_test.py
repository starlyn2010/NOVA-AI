import pygame
import sys

# Dependencias
pygame.init()

class Pong:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Pong - Nova Generated (Fixed)')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        
        # Player dimensions (Paddle)
        self.player_x = 50
        self.player_y = height // 2 - 50
        self.player_width = 20
        self.player_height = 100
        
        # Ball dimensions
        self.ball_x = width // 2
        self.ball_y = height // 2
        self.ball_radius = 15
        self.ball_speed_x = 5
        self.ball_speed_y = 5
        
        # CPU
        self.cpu_x = width - 70
        self.cpu_y = height // 2 - 50

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(text_surface, (x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def game_loop(self):
        while True:
            # Event handling inside loop for responsiveness
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and self.player_y > 0:
                self.player_y -= 5
            if keys[pygame.K_s] and self.player_y < self.height - self.player_height:
                self.player_y += 5
                
            # Ball Logic
            self.ball_x += self.ball_speed_x
            self.ball_y += self.ball_speed_y
            
            # Wall Collision (Top/Bottom)
            if self.ball_y <= 0 or self.ball_y >= self.height - self.ball_radius:
                self.ball_speed_y *= -1
                
            # Score / Reset (Left/Right)
            if self.ball_x <= 0 or self.ball_x >= self.width:
                self.ball_x = self.width // 2
                self.ball_y = self.height // 2
                self.ball_speed_x *= -1 # Serve to winner
                
            # Paddle Collision
            player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)
            cpu_rect = pygame.Rect(self.cpu_x, self.cpu_y, self.player_width, self.player_height)
            ball_rect = pygame.Rect(self.ball_x, self.ball_y, self.ball_radius*2, self.ball_radius*2)
            
            if ball_rect.colliderect(player_rect) or ball_rect.colliderect(cpu_rect):
                self.ball_speed_x *= -1
                
            # CPU Logic (Simple AI)
            if self.cpu_y + self.player_height/2 < self.ball_y:
                self.cpu_y += 4
            elif self.cpu_y + self.player_height/2 > self.ball_y:
                self.cpu_y -= 4

            # Drawing
            self.screen.fill((0, 0, 0)) # Clear screen
            
            # Draw Center Line
            pygame.draw.line(self.screen, (255, 255, 255), (self.width // 2, 0), (self.width // 2, self.height))
            
            # Draw Paddles and Ball
            pygame.draw.rect(self.screen, (255, 255, 255), (self.player_x, self.player_y, self.player_width, self.player_height))
            pygame.draw.rect(self.screen, (255, 255, 255), (self.cpu_x, self.cpu_y, self.player_width, self.player_height))
            pygame.draw.circle(self.screen, (255, 0, 0), (int(self.ball_x), int(self.ball_y)), self.ball_radius)
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Pong()
    while True:
        game.handle_events()
        game.game_loop()

        # Limitar el tiempo de ejecución
        game.clock.tick(60)
