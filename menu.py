import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LEGENDARY GESTURE WAR")

clock = pygame.time.Clock()

# Load assets
background = pygame.image.load("assets/background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

plane = pygame.image.load("assets/plane4.png")
plane = pygame.transform.scale(plane, (120, 120))

pygame.mixer.music.load("assets/music.mp3")
pygame.mixer.music.play(-1)

title_font = pygame.font.SysFont("Arial", 60)
button_font = pygame.font.SysFont("Arial", 36)

def animated_menu():

    fade_alpha = 255
    angle = 0

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if start_button.collidepoint(mouse_pos):
                    return  # start game

                if quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        # Moving background effect
        bg_offset = math.sin(pygame.time.get_ticks() * 0.001) * 20
        screen.blit(background, (0, bg_offset))

        # Floating plane animation
        angle += 0.05
        float_y = HEIGHT//2 - 100 + math.sin(angle) * 20
        screen.blit(plane, (WIDTH//2 - 60, float_y))

        # Pulsing title glow
        glow = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 255
        title = title_font.render("LEGENDARY GESTURE WAR", True, (255, glow, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        # Buttons
        mouse = pygame.mouse.get_pos()

        start_button = pygame.Rect(WIDTH//2 - 100, 400, 250, 60)
        quit_button = pygame.Rect(WIDTH//2 - 100, 480, 200, 60)

        pygame.draw.rect(screen, (0,200,0) if start_button.collidepoint(mouse) else (0,120,0), start_button)
        pygame.draw.rect(screen, (200,0,0) if quit_button.collidepoint(mouse) else (120,0,0), quit_button)

        start_text = button_font.render("START GAME", True, (255,255,255))
        quit_text = button_font.render("QUIT", True, (255,255,255))

        screen.blit(start_text, (start_button.x + 30, start_button.y + 15))
        screen.blit(quit_text, (quit_button.x + 60, quit_button.y + 15))

        # Fade in effect
        if fade_alpha > 0:
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.set_alpha(fade_alpha)
            fade_surface.fill((0,0,0))
            screen.blit(fade_surface, (0,0))
            fade_alpha -= 5

        pygame.display.update()