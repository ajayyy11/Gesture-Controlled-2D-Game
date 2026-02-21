import pygame
import random
import json
from hand_control import HandTracker
from menu import animated_menu

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LEGENDARY GESTURE WAR")

clock = pygame.time.Clock()

# ================= ASSETS =================
plane_img = pygame.image.load("assets/plane4.png")
plane_img = pygame.transform.scale(plane_img, (80, 80))

enemy_img = pygame.image.load("assets/enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (70, 70))

background = pygame.image.load("assets/background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
pygame.mixer.music.load("assets/music.mp3")
pygame.mixer.music.play(-1)

font = pygame.font.SysFont("Arial", 28)

# ================= GAME STATE =================
plane_x = WIDTH // 2
plane_y = HEIGHT - 100

bullets = []
enemy_bullets = []
enemies = []

score = 0
combo = 0
player_health = 5
shield_timer = 0
slow_motion_timer = 0
ultimate_charge = 0
boss_mode = False

game_over = False

# ================= HIGH SCORE =================
try:
    with open("highscore.json", "r") as f:
        high_score = json.load(f)["highscore"]
except:
    high_score = 0

# ================= HAND TRACKER =================
tracker = HandTracker()
animated_menu()

# ================= FUNCTIONS =================
def spawn_enemy():
    x = random.randint(0, WIDTH - 70)
    enemies.append([x, -70, random.randint(3, 6)])

def spawn_boss():
    global boss_mode
    boss_mode = True
    enemies.append([WIDTH//2 - 100, -150, 2, 50])  # boss has 50 HP

# ================= MAIN LOOP =================
running = True
spawn_timer = 0

while running:
    clock.tick(60)

    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if game_over:
        over_text = font.render("GAME OVER - Press R to Restart", True, (255,0,0))
        screen.blit(over_text, (WIDTH//2-200, HEIGHT//2))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            pygame.quit()
            exit()
        pygame.display.update()
        continue

    # ================= HAND INPUT =================
    hand_data = tracker.get_hand_data()
    if hand_data:
        plane_x = hand_data["x"]
        gesture = hand_data["gesture"]

        if gesture == "pinch":
            bullets.append([plane_x+35, plane_y])
            shoot_sound.play()

        if gesture == "fist" and ultimate_charge >= 100:
            bullets.append(["ULTIMATE"])
            ultimate_charge = 0

        if gesture == "open":
            shield_timer = 120

    # ================= SLOW MOTION =================
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and slow_motion_timer <= 0:
        slow_motion_timer = 120

    speed_multiplier = 0.4 if slow_motion_timer > 0 else 1
    if slow_motion_timer > 0:
        slow_motion_timer -= 1

    # ================= SHIELD =================
    if shield_timer > 0:
        shield_timer -= 1

    # ================= SPAWN ENEMIES =================
    spawn_timer += 1
    if spawn_timer > 40:
        spawn_enemy()
        spawn_timer = 0

    if score > 100 and not boss_mode:
        spawn_boss()

    # ================= MOVE ENEMIES =================
    for e in enemies[:]:
        if len(e) == 3:
            e[1] += e[2] * speed_multiplier
            screen.blit(enemy_img, (e[0], e[1]))
        else:
            e[1] += e[2]
            pygame.draw.rect(screen, (200,0,200), (e[0], e[1], 200, 120))

        if e[1] > HEIGHT:
            enemies.remove(e)

        if random.randint(0,100) < 2:
            enemy_bullets.append([e[0]+35, e[1]+70])

    # ================= MOVE PLAYER BULLETS =================
    for b in bullets[:]:
        if b == ["ULTIMATE"]:
            pygame.draw.rect(screen, (0,255,255), (0,0,WIDTH,HEIGHT))
            enemies.clear()
            combo += 10
            bullets.remove(b)
            continue

        b[1] -= 10
        pygame.draw.rect(screen, (255,255,0), (b[0], b[1], 6, 20))
        if b[1] < 0:
            bullets.remove(b)

    # ================= MOVE ENEMY BULLETS =================
    plane_rect = pygame.Rect(plane_x, plane_y, 80, 80)

    for eb in enemy_bullets[:]:
        eb[1] += 8 * speed_multiplier
        pygame.draw.rect(screen, (255,0,0), (eb[0], eb[1], 6, 20))
        if eb[1] > HEIGHT:
            enemy_bullets.remove(eb)

        if pygame.Rect(eb[0], eb[1], 6, 20).colliderect(plane_rect):
            if shield_timer <= 0:
                player_health -= 1
            enemy_bullets.remove(eb)

    # ================= COLLISION =================
    for e in enemies[:]:
        enemy_rect = pygame.Rect(e[0], e[1], 70, 70)

        for b in bullets[:]:
            if b != ["ULTIMATE"]:
                bullet_rect = pygame.Rect(b[0], b[1], 6, 20)
                if bullet_rect.colliderect(enemy_rect):
                    bullets.remove(b)

                    if len(e) == 4:
                        e[3] -= 5
                        if e[3] <= 0:
                            enemies.remove(e)
                            score += 50
                    else:
                        enemies.remove(e)
                        score += 10
                        combo += 1
                        ultimate_charge += 5

        if enemy_rect.colliderect(plane_rect):
            if shield_timer <= 0:
                player_health -= 1
            enemies.remove(e)

    # ================= UI =================
    screen.blit(plane_img, (plane_x, plane_y))

    if shield_timer > 0:
        pygame.draw.circle(screen, (0,255,255), (plane_x+40, plane_y+40), 60, 3)

    score_text = font.render(f"Score: {score}", True, (255,255,255))
    combo_text = font.render(f"Combo: {combo}", True, (255,200,0))
    health_text = font.render(f"HP: {player_health}", True, (255,100,100))
    ult_text = font.render(f"ULT: {ultimate_charge}%", True, (0,255,255))
    high_text = font.render(f"High Score: {high_score}", True, (200,200,200))

    screen.blit(score_text, (10, 10))
    screen.blit(combo_text, (10, 40))
    screen.blit(health_text, (10, 70))
    screen.blit(ult_text, (10, 100))
    screen.blit(high_text, (10, 130))

    if player_health <= 0:
        game_over = True
        if score > high_score:
            high_score = score
            with open("highscore.json", "w") as f:
                json.dump({"highscore": high_score}, f)

    pygame.display.update()

tracker.release()
pygame.quit()