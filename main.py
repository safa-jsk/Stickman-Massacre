from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

import math
import random
import time

# System Congiguration
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_LENGTH = 600
fovY = 120

# Camera-related variables
camera_pos = [0, 600, 600]
camera_angle = 0
camera_radius = 600
camera_height = 600

# Modes
mode_over = False
game_over = False
game_score = 0
bullets_missed = 0
Player_Max_Life = 10
Bar_len  = 20

# Game Progression
level = 1
kills_since_boss = 0

# Enemy-related variables
KILLS_PER_BOSS  = 4
ENEMY_BASE_HP   = 1.0
ENEMY_HP_BONUS  = 0.5
BOSS_BASE_HP    = 10.0
BOSS_HP_BONUS   = 5.0

# Loot state
loot_list = []    # will hold dicts for each on‐screen pickup
last_loot_spawn = 0
next_loot_delay = 0
spawned_a_loot = False

# Effect state
double_active     = False
double_ends       = 0
shield_active     = False
shield_ends       = 0
shield_hits       = 0

# Constants
LOOT_TYPES       = ['life', 'double', 'shield']
LOOT_VIS_TIME    = 10_000    # ms on ground
SHIELD_DURATION  = 15_000    # ms after pickup
DOUBLE_DURATION  = 15_000    # ms after pickup
SHIELD_HITS      = 1
LOOT_SPAWN_MIN   = 5_000     # ms
LOOT_SPAWN_MAX   = 15_000    # ms

# Player-related variables
player_pos = [0, 0, 0]
player_angle = 0
player_speed = 10
player_turn_speed = 5
player_life = 10
shift_count = 0

# Light Attack
right_arm_angle = 0
is_light_attacking = False
light_attack_speed = 2

# Boss Attack
boss_arm_angle = 0
is_boss_attacking = False
boss_attack_speed = 2

# Enemy-related variables
enemy_list = []
enemy_speed = 0.1
enemy_count = 5

# Gun-related variables
bullet_speed = 2
bullet_size = 20
bullets_list = []

# Boss-related variables
boss_spawned = False
boss_position = [0, -500, 0]
boss_grab_toggle = 0
boss_max_health = 5
boss_health     = 5
boss_speed = 0.15

#---------------------------------------------------- Game Space  ---------------------------------------------------

def draw_text(x, y, text, font = GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_tile(x, y, color):
    glColor3f(*color)
    glVertex3f(x, y, 0)
    glVertex3f(x + 100, y, 0)  # tile size is 100x100
    glVertex3f(x + 100, y + 100, 0)
    glVertex3f(x, y + 100, 0)

def draw_arena():
    glBegin(GL_QUADS)
    for x in range(-GRID_LENGTH, GRID_LENGTH + 1, 100): 
        for y in range(-GRID_LENGTH, GRID_LENGTH + 1, 100):
            # Alternate between two metallic-themed shades
            draw_tile(x, y, (0.2, 0.2, 0.25) if ((x + y) // 100) % 2 == 0 else (0.3, 0.3, 0.35))
    glEnd()

    walls = [
        ((0.4, 0.8, 0.3), [(-GRID_LENGTH, -GRID_LENGTH), (-GRID_LENGTH, GRID_LENGTH+100)]),        # Left wall - Lime green
        ((0.2, 0.6, 1.0), [(GRID_LENGTH+100, -GRID_LENGTH), (GRID_LENGTH+100, GRID_LENGTH+100)]),  # Right wall - Neon blue
        ((1.0, 0.4, 0.4), [(-GRID_LENGTH, -GRID_LENGTH), (GRID_LENGTH+100, -GRID_LENGTH)]),        # Top wall - Bright red
        ((1.0, 1.0, 0.3), [(-GRID_LENGTH, GRID_LENGTH+100), (GRID_LENGTH+100, GRID_LENGTH+100)])   # Bottom wall - Yellow
    ]

    glBegin(GL_QUADS)
    for color, (v1, v2) in walls:
        glColor3f(*color)
        glVertex3f(*v1, 0)
        glVertex3f(*v2, 0)
        glVertex3f(*v2, 100)
        glVertex3f(*v1, 100)
    glEnd()

def setup_camera():
    global camera_pos, camera_angle, camera_radius, camera_height, fovY
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, float(WINDOW_WIDTH) / float(WINDOW_HEIGHT), 0.1, 1500)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    angle_rad = math.radians(camera_angle)
    
    x = camera_radius * math.sin(angle_rad)
    y = camera_radius * math.cos(angle_rad)
    z = camera_height
    
    gluLookAt(x, y, z,  # Camera position
            0, 0, 0,    # Look-at target
            0, 0, 1)    # Up vector (z-axis)

def convert_angle_to_radians(angle):
    radian = math.radians(angle)
    cos_value = math.cos(radian)
    sin_value = math.sin(radian)
    return radian, cos_value, sin_value

def dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

#---------------------------------------------------- Player ---------------------------------------------------

def draw_player():
    global gun_point
    
    glPushMatrix()

    # Player Position
    glTranslatef(*player_pos)
    glRotatef(player_angle, 0, 0, 1)  # Rotate around z-axis
    glScalef(2.0, 2.0, 2.0)
    if mode_over:
        glRotatef(-90, 1, 0, 0)

    # Right Leg (Pants)
    glTranslatef(15, 0, 0)      # At (15, 0, 0)
    glColor3f(0.0, 0.0, 0.8)    # Charcoal gray pants
    gluCylinder(gluNewQuadric(), 10, 10, 50, 10, 10)

    # Left Leg (Pants)
    glTranslatef(-30, 0, 0)     # At (-15, 0, 0)
    glColor3f(0.0, 0.0, 0.8)    # Charcoal gray pants
    gluCylinder(gluNewQuadric(), 10, 10, 50, 10, 10)

    # Body (Shirt)
    glTranslatef(15, 0, 50 + 20)    # At (0, 0, 70)
    glColor3f(0.2, 0.0, 0.0)        # Dark red shirt
    glutSolidCube(40)

    # Head
    glTranslatef(0, 0, 40)          # At (0, 0, 110)
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 20, 10, 10)

    # Left Arm / Gun
    glTranslatef(20, 0, -30)        # At (20, 0, 80)
    glRotatef(90, 1, 0, 0)
    glColor3f(254 / 255, 223 / 255, 188 / 255)
    gluCylinder(gluNewQuadric(), 8, 8, 65, 10, 10)

    # Right Arm
    glRotatef(90, 1, 0, 0)
    glTranslatef(-40, 0, 0)
    glRotatef(-90 + right_arm_angle, 1, 0, 0)
    glColor3f(254 / 255, 223 / 255, 188 / 255)
    gluCylinder(gluNewQuadric(), 8, 8, 65, 10, 10)

    glPopMatrix()
    
    gun_point = [20, 0, 70]

def light_attack():
    global is_light_attacking, right_arm_angle
    
    if not mode_over and not is_light_attacking:
        is_light_attacking = True
        right_arm_angle = 0

def draw_bullet(bullet):
    glPushMatrix()
    glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2] + 55)
    glRotatef(90, 1, 0, 0)  # Rotate around z-axis
    glColor3f(1, 0, 0)
    glutSolidCube(bullet_size)
    glPopMatrix()

def fire_bullet():
    angle_rad = convert_angle_to_radians(player_angle - 90)[0]
    
    offset_x = gun_point[0] * math.cos(angle_rad) - gun_point[1] * math.sin(angle_rad)
    offset_y = gun_point[0] * math.sin(angle_rad) + gun_point[1] * math.cos(angle_rad)
    
    x = player_pos[0] + offset_x
    y = player_pos[1] + offset_y
    z = player_pos[2] + gun_point[2]
    
    e_bullet = {'pos': [x, y, z],
                'angle': player_angle-90,
                'speed': bullet_speed}
    bullets_list.append(e_bullet)
    
def move_bullet():
    global bullets_list, bullets_missed
    new_bullets = []
    for i in bullets_list:
        val = convert_angle_to_radians(i['angle'])  
        i['pos'][0] += i['speed'] * val[1]
        i['pos'][1] += i['speed'] * val[2]
        
        if not (i['pos'][0] > GRID_LENGTH + 100
        or i['pos'][0] < -GRID_LENGTH 
        or i['pos'][1] > GRID_LENGTH + 100
        or i['pos'][1] < -GRID_LENGTH):
            new_bullets.append(i)
            
    bullets_list = new_bullets

#---------------------------------------------------- Loots ---------------------------------------------------

def draw_loots():
    """Render each loot as a rotating shape."""
    #print player_pos, loot_list postion
    # if loot_list:
    #     print("Player Position: ", player_pos)
    #     print("Loots Position: ", loot_list)
    for L in loot_list:
        glPushMatrix()
        glTranslatef(L['pos'][0], L['pos'][1], L['pos'][2])
        glRotatef(L['angle'], 0, 0, 1)  # Rotate around z-axis
        glRotatef(L['angle'], 0,1,0)

        if L['type'] == 'life':
            glColor3f(0,1,0)
            glutSolidSphere(35,12,12) # parameters are: radius, slices, stacks
        elif L['type'] == 'double':
            glColor3f(1,1,0)
            glutSolidCube(50) # parameters are: size of the cube
        elif L['type'] == 'shield':
            glColor3f(0,0,1)
            glutSolidTorus(5,30,12,12) # parameters are: inner radius, outer radius, slices, stacks

        glPopMatrix()

def spawn_loot():
    # Create one loot at a random grid position.
    
    now = glutGet(GLUT_ELAPSED_TIME)
    t = random.choice(LOOT_TYPES)
    x = random.uniform(-GRID_LENGTH+100, GRID_LENGTH-100)
    y = random.uniform(-GRID_LENGTH+100, GRID_LENGTH-100)
    loot_list.append({
        'type': t,
        'pos': [x,y,35],           # z=20 so it’s above the ground
        'born': now,
        'angle': 0
    })
    print("Loot Spawned: ", loot_list[0]['type'], loot_list[0]['pos'])

def update_loots():
    # Rotate, expire, and check pickup collisions.
    global last_loot_spawn, double_active, shield_active, player_life, shield_hits, player_pos, loot_list, double_ends, shield_ends, shield_active, shield_hits

    now = glutGet(GLUT_ELAPSED_TIME)

    #  -- spawn new loot?
    if now - (last_loot_spawn+ 5000) >= next_loot_delay:
        if spawned_a_loot:
            pass
        else:
            spawn_loot()      # spawn a new loot
            last_loot_spawn = now
            schedule_next_loot()     

    loots_to_pick = []
    for L in loot_list:
        age = now - L['born']
        if age > LOOT_VIS_TIME:
            continue    # expired, don’t keep

        # rotate 360° every 5s
        L['angle'] = (age / 5000.0) * 360 % 360

        # collision?
        if dist(player_pos, L['pos']) < 40:
            # pickup!
            if L['type'] == 'life':
                heal = int(Player_Max_Life * 0.2)
                player_life = min(Player_Max_Life, player_life + heal)
            elif L['type'] == 'double':
                double_active = True
                double_ends   = now + DOUBLE_DURATION
            elif L['type'] == 'shield':
                shield_active = True
                shield_ends   = now + SHIELD_DURATION
                shield_hits   = SHIELD_HITS
            # remove that loot from the list
            loot_list.remove(L)
            continue  # remove from screen

        loots_to_pick.append(L)
    loot_list[:] = loots_to_pick

    # expire effects
    if double_active and now >= double_ends:
        double_active = False
    if shield_active and now >= shield_ends:
        shield_active = False
    return loots_to_pick

def schedule_next_loot():
    global next_loot_delay
    next_loot_delay = random.randint(LOOT_SPAWN_MIN, LOOT_SPAWN_MAX)   # here we set the delay for the next loot spawn

#---------------------------------------------------- Enemy ---------------------------------------------------

def draw_enemy(x, y, z):
    glPushMatrix()
    
    # Position enemy
    glTranslatef(x, y, z)

    # Calculate rotation angle to face player
    dx = player_pos[0] - x
    dy = player_pos[1] - y
    angle = math.degrees(math.atan2(dy, dx)) - 90
    glRotatef(angle, 0, 0, 1)

    glScalef(2.2, 2.2, 2.2)
    # glPopMatrix()
    # Feet
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(10, -10, 0)
    glutSolidCube(10)
    glTranslatef(-20, 0, 0)
    glutSolidCube(10)
    glPopMatrix()
    
    # Legs
    glPushMatrix()
    glColor3f(0.6, 0.1, 0.1)
    glTranslatef(10, -10, 10)
    gluCylinder(gluNewQuadric(), 5, 5, 20, 10, 10)
    glTranslatef(-20, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 5, 20, 10, 10)
    glPopMatrix()

    # Body (with armor-like cube chest)
    glPushMatrix()
    glColor3f(0.9, 0.2, 0.2)  # Deep red
    glTranslatef(0, 0, 40)
    glScalef(1.5, 1.0, 1.5)
    glutSolidCube(30)
    glPopMatrix()

    # Head (slightly forward and above body)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)  # Dark head
    glTranslatef(0, 0, 60)
    gluSphere(gluNewQuadric(), 10, 10, 10)
    glPopMatrix()

    # Eyes
    glPushMatrix()
    glColor3f(0, 1, 1)  # Cyan glowing eyes
    glTranslatef(-4, 10, 63)
    glutSolidCube(3)
    glTranslatef(8, 0, 0)
    glutSolidCube(3)
    glPopMatrix()

    # Left Arm
    glPushMatrix()
    glColor3f(0.5, 0.2, 0.2)
    glTranslatef(20, 0, 45)  # Side of body
    glRotatef(-90, 1, 0, 0)  # Pointing forward like player
    gluCylinder(gluNewQuadric(), 4, 4, 25, 10, 10)
    glPopMatrix()

    # Right Arm
    glPushMatrix()
    glColor3f(0.5, 0.2, 0.2)
    glTranslatef(-20, 0, 45)  # Side of body
    glRotatef(-90, 1, 0, 0)  # Same rotation
    gluCylinder(gluNewQuadric(), 4, 4, 25, 10, 10)
    glPopMatrix()

    glPopMatrix()

def spawn_enemy(num=enemy_count):
    global enemy_list
    margin = 100  # Safety margin from arena edges

    while len(enemy_list) < num:
        x = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
        y = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)

        while abs(x) < player_pos[0] + 200:
            x = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
        while abs(y) < player_pos[1] + 200:
            y = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
        
        enemy_list.append([x, y, 0])

def move_enemy():
    global enemy_list, enemy_speed, game_over, player_life
    global mode_over, shield_active, shield_hits
    
    for enemy in enemy_list:
        if mode_over:
            break
        
        # Calculate angle to player
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]

        radian = math.atan2(dy, dx)
        
        enemy[0] += enemy_speed * math.cos(radian)
        enemy[1] += enemy_speed * math.sin(radian)

        # Check for collision with player
        if dist(player_pos, enemy) < 50:
            if shield_active:
                shield_hits -= 1
                if shield_hits <= 0:
                    shield_active = False
            else:
                player_life -= 1
                if player_life <= 0:
                    game_over = True
            spawn_enemy(1)
            enemy_list.remove(enemy)
    
#---------------------------------------------------- Boss ---------------------------------------------------   
   
def draw_boss(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(3.5,3.5, 3.5)

    quad = gluNewQuadric()

    # === Legs ===
    for leg_x in [15, -15]:
        glPushMatrix()
        glTranslatef(leg_x, 0, 0)
        glColor3f(0.2, 0.2, 0.2)
        gluCylinder(quad, 10, 10, 50, 10, 10)
        glPopMatrix()

    # === Body ===
    glPushMatrix()
    glTranslatef(0, 0, 70)
    glColor3f(0.25, 0.0, 0.4)
    glutSolidCube(40)
    glPopMatrix()

    # === Head ===
    glPushMatrix()
    glTranslatef(0, 0, 110)
    glColor3f(0.2, 0.2, 0.2)
    gluSphere(quad, 20, 10, 10)
    glPopMatrix()

    # === Eyes ===
    glPushMatrix()
    glColor3f(0.0, 1.0, 1.0)
    glTranslatef(-5, 18, 118)
    glutSolidSphere(2.5, 10, 10)
    glTranslatef(10, 0, 0)
    glutSolidSphere(2.5, 10, 10)
    glPopMatrix()

    # === Teeth (visible, facing player) ===
    glPushMatrix()
    glTranslatef(-6, 18.5, 108)  # In front of head, near mouth
    glRotatef(-90, 1, 0, 0)      # Point teeth downward
    for i in range(4):
        glPushMatrix()
        glTranslatef(i * 4, 0, 0)
        glColor3f(1.0, 1.0, 1.0)
        glutSolidCone(1.5, 4, 6, 2)
        glPopMatrix()
    glPopMatrix()

    # === Horns ===
    for side in [-10, 10]:
        glPushMatrix()
        glColor3f(0.75, 0.75, 0.75)
        glTranslatef(side, -5, 125)
        glRotatef(-45 if side < 0 else 45, 1, 0, 0)
        gluCylinder(quad, 2, 0, 20, 8, 8)
        glPopMatrix()

        # === LEFT ARM (close to shoulder like player) ===
        glPushMatrix()
        glTranslatef(20, 0, 80)  # Move closer to body, lower to match shoulder height
        glRotatef(-90, 1, 0, 0)
        
        glPushMatrix()
        glRotatef(boss_arm_angle, 0, 1, 0)  # Rotate around y-axis
        glColor3f(0.5, 0.0, 0.0)  # Crimson
        gluCylinder(quad, 8, 8, 65, 10, 10)
        glPopMatrix()
        
        glPopMatrix()

        # Caps
        glPushMatrix()
        glTranslatef(0, 0, 65)
        glColor3f(0.2, 0.2, 0.2)
        gluDisk(quad, 0, 8, 10, 1)
        glPopMatrix()

        glPushMatrix()
        glRotatef(180, 1, 0, 0)
        gluDisk(quad, 0, 8, 10, 1)
        glPopMatrix()
        # glPopMatrix()

        # === RIGHT ARM (close to shoulder like player) ===
        glPushMatrix()
        glTranslatef(-20, 0, 80)  # Move closer to body
        glRotatef(-90, 1, 0, 0)
        
        glPushMatrix()
        glRotatef(-boss_arm_angle, 0, 1, 0)  # Rotate around y-axis
        glColor3f(0.5, 0.0, 0.0)
        gluCylinder(quad, 8, 8, 65, 10, 10)
        glPopMatrix()
        
        glPopMatrix()

        # Caps
        glPushMatrix()
        glTranslatef(0, 0, 65)
        glColor3f(0.2, 0.2, 0.2)
        gluDisk(quad, 0, 8, 10, 1)
        glPopMatrix()

        glPushMatrix()
        glRotatef(180, 1, 0, 0)
        gluDisk(quad, 0, 8, 10, 1)
        glPopMatrix()
    glPopMatrix()

def move_boss():
    global boss_position, boss_health, boss_active, kills_since_boss, boss_spawned, boss_speed, boss_angle, game_over, player_pos, shield_active, shield_hits, player_life, mode_over, is_boss_attacking, boss_arm_angle, enemy_count, level
    
    if boss_spawned:
        # Move boss towards player
        dx = player_pos[0] - boss_position[0]
        dy = player_pos[1] - boss_position[1]
        
        boss_angle = math.degrees(math.atan2(dy, dx)) 
        angle_rad = math.atan2(dy, dx)
        
        boss_position[0] += boss_speed * math.cos(angle_rad)
        boss_position[1] += boss_speed * math.sin(angle_rad)
        
        # Check for collision with player
        if dist(player_pos, boss_position) < 50:
            boss_attack()
            if shield_active:
                shield_hits -= 1
                if shield_hits <= 0:
                    shield_active = False
            else:
                player_life -= 2
                if player_life <= 0:
                    game_over = True
                player_pos[0] += 300 * math.cos(angle_rad)
                player_pos[1] += 300 * math.sin(angle_rad)
        
        # Check if boss is out of bounds
        if (boss_position[0] > GRID_LENGTH + 100 or boss_position[0] < -GRID_LENGTH or
            boss_position[1] > GRID_LENGTH + 100 or boss_position[1] < -GRID_LENGTH):
            boss_position[0] = max(-GRID_LENGTH, min(boss_position[0], GRID_LENGTH + 100))
            boss_position[1] = max(-GRID_LENGTH, min(boss_position[1], GRID_LENGTH + 100))
        # Check if boss is dead
        if boss_health <= 0:
            boss_active = False
            kills_since_boss += 1
            boss_spawned = False
            boss_health = boss_max_health
            boss_position = [0, -500, 0]
            enemy_count += 1
            level += 1
            spawn_enemy(enemy_count)
        
def boss_attack():
    global is_boss_attacking, boss_arm_angle, boss_attack_time, boss_attack_duration
    
    if not mode_over and not is_boss_attacking:
        is_boss_attacking = True
        boss_arm_angle = 0
        boss_attack_time = time.time()

#---------------------------------------------------- Moves ---------------------------------------------------  
def hit_enemy_bullet(bullets, enemies):
    global game_score, bullets_missed, enemy_list, boss_health, boss_active, kills_since_boss, boss_spawned, enemy_count, boss_position, level, boss_max_health
    
    for bullet in bullets:
        for enemy in enemies:
            if dist(bullet['pos'], enemy) <= 50:  # Assuming a hit if within 50 
                game_score += 1
                bullets_missed += 1
                bullets.remove(bullet)
                enemies.remove(enemy)

                break
            
        if boss_spawned:
            if dist(bullet['pos'], boss_position) <= 50:
                boss_health -= 1
                bullets.remove(bullet)
                break
    
    if len(enemies) == 0:
        boss_spawned = True

def in_front(bx, by, bz):
    dx = player_pos[0] - bx
    dy = player_pos[1] - by
    target_angle = math.degrees(math.atan2(dy, dx))
    pa = player_angle % 360
    ta = target_angle % 360
    diff = (ta - pa + 540) % 360 - 180
    return abs(diff) <= 90

def hit_enemy_melee(enemies):
    global game_score, bullets_missed, enemy_list, boss_health, boss_active, kills_since_boss, is_light_attacking, boss_spawned, boss_position, level, enemy_count, boss_max_health
    
    # Only check once per swing
    if not is_light_attacking or (right_arm_angle > -90):
        return
    # Hit frame reached: check all enemiesd
    for enemy in enemies[:]:
        if dist(player_pos, enemy) <= 150 and in_front(*enemy):
            game_score += 1
            enemies.remove(enemy)
    
    if boss_spawned:
        if dist(player_pos, boss_position) <= 150 and in_front(*boss_position):
            boss_health -= 1
    
    if len(enemies) == 0:
        boss_spawned = True

#---------------------------------------------------- Inputs ---------------------------------------------------
                   
def mouse_listener(button, state, x, y):
    global mode_over, mode_first_person, player_turn_speed, mode_cheat_vision
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        light_attack()
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # strong_attack()
        fire_bullet()
    
def keyboard_listener(key, a, b):
    global player_angle, player_speed, player_turn_speed, player_pos, gun_angle, gun_bullet_speed, gun_bullets, gun_missed_bullets
    global mode_over, player_life, game_score, enemy_list, mode_cheat, mode_cheat_vision, mode_first_person, enemy_size
    
    x = player_pos[0]
    y = player_pos[1]
    z = player_pos[2]
    
    if not mode_over:
        if key == b'w':
            # Player moves forward
            x -= player_speed * math.sin(math.radians(-player_angle))
            y -= player_speed * math.cos(math.radians(player_angle))
            
            if x < -GRID_LENGTH:
                x = -GRID_LENGTH
            if x > GRID_LENGTH + 100:
                x = GRID_LENGTH + 100
            if y < -GRID_LENGTH:
                y = -GRID_LENGTH
            if y > GRID_LENGTH + 100:
                y = GRID_LENGTH + 100
        
        if key == b's':
            # Player moves backward
            x += player_speed * math.sin(math.radians(-player_angle))
            y += player_speed * math.cos(math.radians(player_angle))
            
            if x < -GRID_LENGTH:
                x = -GRID_LENGTH
            if x > GRID_LENGTH + 100:
                x = GRID_LENGTH + 100
            if y < -GRID_LENGTH:
                y = -GRID_LENGTH
            if y > GRID_LENGTH + 100:
                y = GRID_LENGTH + 100
        
        if key == b'a':
            # Player rotates left
            player_angle += player_turn_speed
        
        if key == b'd':
            # Player rotates right
            player_angle -= player_turn_speed
    
    if key == b'p':
        boss_attack()
    
    player_pos = [x, y, z]
    
def specialKeyListener(key, a, b):
    global camera_angle, camera_radius, camera_height, player_speed, player_turn_speed, player_pos, player_angle, game_over, mode_over, enemy_list, bullets_missed, game_score, boss_health, boss_active, kills_since_boss, shift_count
    
    mods = glutGetModifiers()
    
    if key == GLUT_KEY_UP:
        camera_height -= 10
        camera_radius -= 10

    if key == GLUT_KEY_DOWN:
        camera_height += 10
        camera_radius += 10

    if key == GLUT_KEY_LEFT:
        camera_angle -= 5

    if key == GLUT_KEY_RIGHT:
        camera_angle += 5
    
    if mods & GLUT_ACTIVE_SHIFT:
        if (shift_count % 2) == 0:
            player_speed *= 2.0
        else:
            player_speed *= 0.5
        shift_count += 1

#---------------------------------------------------- System ---------------------------------------------------

def show_screen():
    global mode_over, player_life, game_score, gun_missed_bullets, Player_Max_Life, Bar_len, bullets_missed, boss_active, boss_health, boss_max_health, spawned_a_loot,player_score, boss_spawned, boss_position

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setup_camera()
    draw_arena()
    draw_player()
    
    draw_loots()
    spawned_loot = update_loots()
    
    if spawned_loot:
        spawned_a_loot = True
        if spawned_loot[0]['type'] == 'double':
            draw_text(380, 740, f"Loot spawned : DOUBLE DAMAGE")
        else:
            draw_text(380, 740, f"Loot spawned : {(spawned_loot[0]['type']).upper()}")
    else:
        spawned_a_loot = False
        # draw_text(380, 770, f"Loot spawned : None")
    
    # ---- NEW: draw a text-based health bar ----
    hp       = max(0, min(player_life, Player_Max_Life))
    hp_ratio = hp / Player_Max_Life
    filled   = int(hp_ratio * Bar_len)
    empty    = Bar_len - filled
    bar      = '#' * filled + '-' * empty
    player_percent  = int(hp_ratio * 100)
    
    #Boss -----------------------------------------
    if boss_spawned:
    # clamp
        bhp_ratio = max(0.0, boss_health/boss_max_health)
        bfilled   = int(bhp_ratio * Bar_len)
        bbar      = '#' * bfilled + '-' * (Bar_len - bfilled)
        boss_percent   = int(bhp_ratio*100)
        draw_text(680, 770, f"Boss: [{bbar}] {boss_percent}%")
        
    if not game_over:
        draw_text(10, 770, f"HP: [{bar}] {player_percent}%")
        draw_text(10, 740, f"Score: {game_score}")
        draw_text(10, 710, f"Level: {level}")
        
        # draw_text(10, 710, f"Bullets Missed: {bullets_missed}")
    if game_over:
        # draw_text(400, 400, "GAME OVER! Press 'R' to Restart")
        draw_text(10, 770, f"Game is Over. Your score is {game_score}.")
        draw_text(10, 740, 'Press "R" to Restart the Game')
    
    if not mode_over:
        for enemy in enemy_list:
            draw_enemy(*enemy)
    
    for bullet in bullets_list:
        draw_bullet(bullet)
    if boss_spawned:
        draw_boss(*boss_position)

    glutSwapBuffers()

def idle():
    global right_arm_angle, is_light_attacking, left_arm_angle, is_boss_attacking, boss_arm_angle, boss_grab_toggle, player_pos, player_angle, bullets_list, enemy_list, game_over, bullets_missed, game_score, boss_health, boss_active, kills_since_boss, update_loots
    
    if not game_over:
        move_enemy()
        move_bullet()
        
        update_loots() 
        
        hit_enemy_bullet(bullets_list, enemy_list)
        hit_enemy_melee(enemy_list)

        if boss_spawned:
            move_boss()
        
        if is_light_attacking:
            right_arm_angle -= light_attack_speed
            if abs(right_arm_angle) >= 360:
                right_arm_angle = 0
                is_light_attacking = False
        
        if is_boss_attacking:
            boss_arm_angle += boss_attack_speed * 0.5 * (-1) ** boss_grab_toggle
            if abs(boss_arm_angle) >= 90:
                boss_grab_toggle = 1
            if abs(boss_arm_angle) >= 91:
                boss_arm_angle = 0
                is_boss_attacking = False
                boss_grab_toggle = 0
    
    glutPostRedisplay()

def main():
    global last_loot_spawn
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy 3D")
    glEnable(GL_DEPTH_TEST)
    
    schedule_next_loot()  
    last_loot_spawn = glutGet(GLUT_ELAPSED_TIME) 
    spawn_enemy(enemy_count)
    
    glutDisplayFunc(show_screen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouse_listener)
    
    # update_loots()
    
    glutMainLoop()

if __name__ == "__main__":
    main()
