from pathlib import Path
import math

import pygame


BASE_DIR = Path(__file__).resolve().parent


def animated_menu():
    """Show the start menu on the existing display and return whether to start."""
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

    width, height = screen.get_size()
    background_path = BASE_DIR / "assets" / "background.png"
    plane_path = BASE_DIR / "assets" / "plane4.png"
    background = pygame.transform.scale(pygame.image.load(str(background_path)), (width, height))
    plane = pygame.transform.scale(pygame.image.load(str(plane_path)), (120, 120))

    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("Arial", 60)
    button_font = pygame.font.SysFont("Arial", 36)
    fade_alpha = 255
    angle = 0

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                width, height = screen.get_size()
                background = pygame.transform.scale(
                    pygame.image.load(str(background_path)), (width, height)
                )

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = event.pos
                start_button = pygame.Rect(width // 2 - 125, 400, 250, 60)
                quit_button = pygame.Rect(width // 2 - 100, 480, 200, 60)
                if start_button.collidepoint(mouse):
                    return True
                if quit_button.collidepoint(mouse):
                    return False

        bg_offset = math.sin(pygame.time.get_ticks() * 0.001) * 20
        screen.blit(background, (0, bg_offset))

        angle += 0.05
        float_y = height // 2 - 100 + math.sin(angle) * 20
        screen.blit(plane, (width // 2 - 60, float_y))

        glow = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 255
        title = title_font.render("LEGENDARY GESTURE WAR", True, (255, int(glow), 0))
        screen.blit(title, (width // 2 - title.get_width() // 2, 80))

        mouse = pygame.mouse.get_pos()
        start_button = pygame.Rect(width // 2 - 125, 400, 250, 60)
        quit_button = pygame.Rect(width // 2 - 100, 480, 200, 60)

        pygame.draw.rect(
            screen,
            (0, 200, 0) if start_button.collidepoint(mouse) else (0, 120, 0),
            start_button,
        )
        pygame.draw.rect(
            screen,
            (200, 0, 0) if quit_button.collidepoint(mouse) else (120, 0, 0),
            quit_button,
        )

        start_text = button_font.render("START GAME", True, (255, 255, 255))
        quit_text = button_font.render("QUIT", True, (255, 255, 255))
        screen.blit(start_text, (start_button.x + 30, start_button.y + 15))
        screen.blit(quit_text, (quit_button.x + 60, quit_button.y + 15))

        if fade_alpha > 0:
            fade_surface = pygame.Surface((width, height))
            fade_surface.set_alpha(fade_alpha)
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))
            fade_alpha = max(0, fade_alpha - 5)

        pygame.display.update()
