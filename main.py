import json
import random
from pathlib import Path

import cv2
import pygame

from hand_control import HandTracker
from menu import animated_menu

BASE_DIR = Path(__file__).resolve().parent


def load_image(filename, size):
    image_path = BASE_DIR / "assets" / filename
    return pygame.transform.scale(pygame.image.load(str(image_path)), size)


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        # Continue silently if the machine has no usable audio device.
        pass

    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    width, height = screen.get_size()
    pygame.display.set_caption("Gesture Controlled Game - LEGEND MODE")
    clock = pygame.time.Clock()

    plane_img = load_image("plane4.png", (80, 80))
    enemy_img = load_image("enemy.png", (70, 70))
    background = pygame.transform.scale(
        pygame.image.load(str(BASE_DIR / "assets" / "background.png")), (width, height)
    )

    def load_sound(filename):
        try:
            return pygame.mixer.Sound(str(BASE_DIR / "assets" / filename))
        except pygame.error:
            return None

    shoot_sound = load_sound("shoot.wav")
    explode_sound = load_sound("explosion.wav")
    music_path = BASE_DIR / "assets" / "music.mp3"
    if pygame.mixer.get_init() and music_path.is_file():
        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    font = pygame.font.SysFont("Arial", 28)
    plane_x, plane_y = width // 2, height - 120
    bullets, enemy_bullets, enemies, particles = [], [], [], []
    score, combo, player_health = 0, 0, 5
    shield_timer, ultimate_charge = 0, 0
    boss_mode, game_over = False, False
    stars = [[random.randint(0, width), random.randint(0, height), random.randint(1, 3)] for _ in range(80)]

    highscore_path = BASE_DIR / "highscore.json"
    try:
        high_score = int(json.loads(highscore_path.read_text(encoding="utf-8")).get("highscore", 0))
        high_score = max(0, high_score)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        high_score = 0

    tracker = None
    try:
        tracker = HandTracker()
        if not animated_menu():
            return
        running, spawn_timer = True, 0

        def spawn_enemy():
            enemies.append([random.randint(0, width - 70), -70, random.randint(3, 6)])

        def spawn_boss():
            nonlocal boss_mode
            boss_mode = True
            enemies.append([width // 2 - 100, -150, 2, 60])

        def spawn_particles(x, y, color=(255, 200, 0), count=15):
            for _ in range(count):
                particles.append([x, y, random.uniform(-2, 2), random.uniform(-2, 2), random.randint(3, 6), color])

        def play_sound(sound):
            if sound is not None:
                sound.play()

        while running:
            clock.tick(60)
            screen.blit(background, (0, 0))

            for star in stars:
                pygame.draw.circle(screen, (255, 255, 255), (star[0], star[1]), star[2])
                star[1] += 2
                if star[1] > height:
                    star[1] = 0
                    star[0] = random.randint(0, width)

            for particle in particles[:]:
                particle[0] += particle[2]
                particle[1] += particle[3]
                particle[4] -= 0.2
                if particle[4] <= 0:
                    particles.remove(particle)
                else:
                    pygame.draw.circle(screen, particle[5], (int(particle[0]), int(particle[1])), max(1, int(particle[4])))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()

            if game_over:
                over_text = font.render("GAME OVER - Press R to Quit", True, (255, 0, 0))
                screen.blit(over_text, (width // 2 - 200, height // 2))
                if pygame.key.get_pressed()[pygame.K_r]:
                    running = False
                pygame.display.update()
                continue

            hand_data = tracker.get_hand_data()
            gesture = None
            if hand_data:
                plane_x = max(0, min(width - 80, hand_data["x"]))
                gesture = hand_data["gesture"]
                if gesture == "pinch":
                    bullets.append([plane_x + 35, plane_y, []])
                    play_sound(shoot_sound)
                elif gesture == "fist" and ultimate_charge >= 100:
                    bullets.append(["ULTIMATE"])
                    ultimate_charge = 0
                elif gesture == "open":
                    shield_timer = 120

            spawn_timer += 1
            if spawn_timer > 40:
                spawn_enemy()
                spawn_timer = 0
            if score > 120 and not boss_mode:
                spawn_boss()

            plane_rect = pygame.Rect(plane_x, plane_y, 80, 80)

            for enemy in enemies[:]:
                if len(enemy) == 3:
                    enemy[1] += enemy[2]
                    screen.blit(enemy_img, (enemy[0], enemy[1]))
                else:
                    enemy[1] += enemy[2]
                    pygame.draw.rect(screen, (200, 0, 200), (enemy[0], enemy[1], 200, 120))
                if enemy[1] > height and enemy in enemies:
                    enemies.remove(enemy)
                    continue
                if random.randint(0, 100) < 2:
                    enemy_bullets.append([enemy[0] + 35, enemy[1] + 70])

            for bullet in bullets[:]:
                if bullet == ["ULTIMATE"]:
                    pygame.draw.rect(screen, (0, 255, 255), (0, 0, width, height))
                    enemies.clear()
                    combo += 10
                    bullets.remove(bullet)
                    continue
                trail = bullet[2]
                trail.append((bullet[0] + 3, bullet[1] + 10))
                if len(trail) > 5:
                    trail.pop(0)
                for point in trail:
                    pygame.draw.circle(screen, (255, 255, 0), point, 3)
                bullet[1] -= 10
                pygame.draw.rect(screen, (255, 255, 0), (bullet[0], bullet[1], 6, 20))
                if bullet[1] < 0:
                    bullets.remove(bullet)

            for enemy_bullet in enemy_bullets[:]:
                enemy_bullet[1] += 8
                pygame.draw.rect(screen, (255, 0, 0), (enemy_bullet[0], enemy_bullet[1], 6, 20))
                if enemy_bullet[1] > height:
                    enemy_bullets.remove(enemy_bullet)
                    continue
                if pygame.Rect(enemy_bullet[0], enemy_bullet[1], 6, 20).colliderect(plane_rect):
                    if shield_timer <= 0:
                        player_health -= 1
                    enemy_bullets.remove(enemy_bullet)

            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], 70, 70)
                for bullet in bullets[:]:
                    if bullet == ["ULTIMATE"]:
                        continue
                    bullet_rect = pygame.Rect(bullet[0], bullet[1], 6, 20)
                    if bullet_rect.colliderect(enemy_rect):
                        if bullet in bullets:
                            bullets.remove(bullet)
                        spawn_particles(enemy[0] + 35, enemy[1] + 35)
                        play_sound(explode_sound)
                        if len(enemy) == 4:
                            enemy[3] -= 5
                            if enemy[3] <= 0 and enemy in enemies:
                                enemies.remove(enemy)
                                score += 50
                        elif enemy in enemies:
                            enemies.remove(enemy)
                            score += 10
                            combo += 1
                            ultimate_charge = min(100, ultimate_charge + 5)
                        break
                if enemy in enemies and enemy_rect.colliderect(plane_rect):
                    if shield_timer <= 0:
                        player_health -= 1
                    enemies.remove(enemy)

            screen.blit(plane_img, (plane_x, plane_y))
            if shield_timer > 0:
                shield_timer -= 1
                pygame.draw.circle(screen, (0, 255, 255), (plane_x + 40, plane_y + 40), 60, 3)

            screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
            screen.blit(font.render(f"Combo: {combo}", True, (255, 200, 0)), (10, 40))
            screen.blit(font.render(f"HP: {player_health}", True, (255, 100, 100)), (10, 70))
            screen.blit(font.render(f"High Score: {high_score}", True, (200, 200, 200)), (10, 100))
            pygame.draw.rect(screen, (50, 50, 50), (10, 140, 200, 20))
            pygame.draw.rect(screen, (0, 255, 255), (10, 140, 2 * ultimate_charge, 20))
            if gesture:
                screen.blit(font.render(f"Gesture: {gesture}", True, (0, 255, 0)), (width - 250, 10))

            cam_frame = tracker.get_frame()
            if cam_frame is not None:
                cam_frame = cv2.cvtColor(cam_frame, cv2.COLOR_BGR2RGB)
                cam_frame = cv2.flip(cam_frame, 1)
                cam_surface = pygame.surfarray.make_surface(cam_frame.swapaxes(0, 1))
                screen.blit(pygame.transform.scale(cam_surface, (220, 160)), (10, 10))
                pygame.draw.rect(screen, (255, 255, 255), (10, 10, 220, 160), 2)

            if player_health <= 0:
                game_over = True
                if score > high_score:
                    high_score = score
                    highscore_path.write_text(json.dumps({"highscore": high_score}), encoding="utf-8")

            pygame.display.update()
    finally:
        if tracker is not None:
            tracker.release()
        pygame.quit()


if __name__ == "__main__":
    main()
