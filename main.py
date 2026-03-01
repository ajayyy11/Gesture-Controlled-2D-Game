import pygame
import random
import json
from hand_control import HandTracker
from menu import animated_menu
import cv2

pygame.init()
pygame.mixer.init()

# ================= DISPLAY =================
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Gesture Controlled Game - LEGEND MODE")
clock = pygame.time.Clock()

# ================= ASSETS =================
plane_img = pygame.image.load("assets/plane4.png")
plane_img = pygame.transform.scale(plane_img, (80, 80))
enemy_img = pygame.image.load("assets/enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (70, 70))
background = pygame.image.load("assets/background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
explode_sound = pygame.mixer.Sound("assets/explosion.wav")
pygame.mixer.music.load("assets/music.mp3")
pygame.mixer.music.play(-1)
font = pygame.font.SysFont("Arial", 28)

# ================= GAME VARIABLES =================
plane_x, plane_y = WIDTH//2, HEIGHT - 120
bullets, enemy_bullets, enemies = [], [], []
particles = []
score, combo, player_health = 0, 0, 5
shield_timer, ultimate_charge = 0, 0
boss_mode, game_over = False, False
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1,3)] for _ in range(80)]

# ================= HIGH SCORE =================
try:
    with open("highscore.json","r") as f:
        high_score = json.load(f)["highscore"]
except:
    high_score = 0

# ================= HAND TRACKER =================
tracker = HandTracker()
animated_menu()

# ================= FUNCTIONS =================
def spawn_enemy():
    x = random.randint(0, WIDTH - 70)
    enemies.append([x, -70, random.randint(3,6)])

def spawn_boss():
    global boss_mode
    boss_mode = True
    enemies.append([WIDTH//2 - 100, -150, 2, 60])

def draw_stars():
    for star in stars:
        pygame.draw.circle(screen, (255,255,255), (star[0], star[1]), star[2])
        star[1] += 2
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)

def draw_ui(gesture):
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10, 10))
    screen.blit(font.render(f"Combo: {combo}", True, (255,200,0)), (10, 40))
    screen.blit(font.render(f"HP: {player_health}", True, (255,100,100)), (10, 70))
    screen.blit(font.render(f"High Score: {high_score}", True, (200,200,200)), (10, 100))
    pygame.draw.rect(screen, (50,50,50), (10, 140, 200, 20))
    pygame.draw.rect(screen, (0,255,255), (10, 140, 2*ultimate_charge, 20))
    if gesture:
        screen.blit(font.render(f"Gesture: {gesture}", True, (0,255,0)), (WIDTH-250, 10))

# ================= PARTICLES =================
def spawn_particles(x, y, color=(255,200,0), count=15):
    for _ in range(count):
        particles.append([x, y, random.uniform(-2,2), random.uniform(-2,2), random.randint(3,6), color])

def update_particles():
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 0.2
        if p[4] <=0: particles.remove(p)
        else: pygame.draw.circle(screen, p[5], (int(p[0]), int(p[1])), int(p[4]))

# ================= MAIN LOOP =================
running, spawn_timer = True, 0

while running:
    clock.tick(60)
    screen.blit(background, (0,0))
    draw_stars()
    update_particles()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f: pygame.display.toggle_fullscreen()

    if game_over:
        over_text = font.render("GAME OVER - Press R to Restart", True, (255,0,0))
        screen.blit(over_text, (WIDTH//2-200, HEIGHT//2))
        if pygame.key.get_pressed()[pygame.K_r]:
            pygame.quit()
            exit()
        pygame.display.update()
        continue

    # ================= HAND INPUT =================
    hand_data = tracker.get_hand_data()
    gesture = None
    if hand_data:
        plane_x = hand_data["x"]
        gesture = hand_data["gesture"]
        color = hand_data["color"]

        if gesture == "pinch":
            bullets.append([plane_x+35, plane_y, []])  # store trail
            shoot_sound.play()
        elif gesture == "fist" and ultimate_charge >= 100:
            bullets.append(["ULTIMATE"])
            ultimate_charge = 0
        elif gesture == "open":
            shield_timer = 120

    # ================= SPAWN =================
    spawn_timer += 1
    if spawn_timer > 40: spawn_enemy(); spawn_timer=0
    if score > 120 and not boss_mode: spawn_boss()

    plane_rect = pygame.Rect(plane_x, plane_y, 80, 80)

    # ================= MOVE ENEMIES =================
    for e in enemies[:]:
        if len(e)==3: e[1]+=e[2]; screen.blit(enemy_img,(e[0],e[1]))
        else: e[1]+=e[2]; pygame.draw.rect(screen,(200,0,200),(e[0],e[1],200,120))
        if e[1] > HEIGHT: enemies.remove(e)
        if random.randint(0,100)<2: enemy_bullets.append([e[0]+35,e[1]+70])

    # ================= MOVE BULLETS =================
    for b in bullets[:]:
        if b==["ULTIMATE"]: pygame.draw.rect(screen,(0,255,255),(0,0,WIDTH,HEIGHT)); enemies.clear(); combo+=10; bullets.remove(b); continue
        # Bullet trail
        trail = b[2]
        trail.append((b[0]+3,b[1]+10))
        if len(trail)>5: trail.pop(0)
        for t in trail: pygame.draw.circle(screen,(255,255,0), t, 3)
        b[1]-=10
        pygame.draw.rect(screen,(255,255,0),(b[0],b[1],6,20))
        if b[1]<0: bullets.remove(b)

    # ================= ENEMY BULLETS =================
    for eb in enemy_bullets[:]:
        eb[1]+=8
        pygame.draw.rect(screen,(255,0,0),(eb[0],eb[1],6,20))
        if eb[1]>HEIGHT: enemy_bullets.remove(eb)
        if pygame.Rect(eb[0],eb[1],6,20).colliderect(plane_rect):
            if shield_timer<=0: player_health-=1
            enemy_bullets.remove(eb)

    # ================= COLLISION =================
    for e in enemies[:]:
        enemy_rect = pygame.Rect(e[0],e[1],70,70)
        for b in bullets[:]:
            if b!=["ULTIMATE"]:
                bullet_rect = pygame.Rect(b[0],b[1],6,20)
                if bullet_rect.colliderect(enemy_rect):
                    bullets.remove(b)
                    spawn_particles(e[0]+35,e[1]+35)
                    explode_sound.play()
                    if len(e)==4: e[3]-=5; 
                    if len(e)==4 and e[3]<=0: enemies.remove(e); score+=50
                    if len(e)==3: enemies.remove(e); score+=10; combo+=1; ultimate_charge+=5
        if enemy_rect.colliderect(plane_rect):
            if shield_timer<=0: player_health-=1
            enemies.remove(e)

    # ================= DRAW PLAYER =================
    screen.blit(plane_img,(plane_x,plane_y))
    if shield_timer>0: shield_timer-=1; pygame.draw.circle(screen,(0,255,255),(plane_x+40,plane_y+40),60,3)

    draw_ui(gesture)

    # ================= MINI CAMERA =================
    cam_frame = tracker.get_frame()
    if cam_frame is not None:
        cam_frame = cv2.cvtColor(cam_frame, cv2.COLOR_BGR2RGB)
        cam_frame = cv2.flip(cam_frame, 1)
        cam_surface = pygame.surfarray.make_surface(cam_frame.swapaxes(0,1))
        mini_cam = pygame.transform.scale(cam_surface, (220,160))
        screen.blit(mini_cam, (10,10))
        pygame.draw.rect(screen,(255,255,255),(10,10,220,160),2)

    # ================= GAME OVER CHECK =================
    if player_health<=0:
        game_over=True
        if score>high_score: high_score=score; 
        with open("highscore.json","w") as f: json.dump({"highscore":high_score},f)

    pygame.display.update()

tracker.release()
pygame.quit()