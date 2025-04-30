from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

import math
import random

# System Configuration
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_LENGTH = 600
fovY = 120

# Camera-related variables
camera_pos = [0, 500, 500]
camera_angle = 0
camera_radius = 600
camera_height = 600

# Modes
mode_over = False

# Player-related variables
player_pos = [0, 0, 0]
player_angle = 0
player_speed = 10
player_turn_speed = 5
player_life = 10
player_score = 0

# Light Attack
right_arm_angle = 0
is_light_attacking = False
light_attack_speed = 2

# Strong Attack
left_arm_angle = 0
is_strong_attacking = False
strong_attack_speed = 2

# Enemy-related variables
enemy_list = []
enemy_speed = 5
enemy_count = 5

bullets_list = []

boss_spawned = False
boss_position = [0, 0, 0] 

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

def draw_player():
    glPushMatrix()

    # Player Position
    glTranslatef(*player_pos)
    glRotatef(player_angle, 0, 0, 1)  # Rotate around z-axis
    glScalef(2.0, 2.0, 2.0)
    if mode_over:
        glRotatef(-90, 1, 0, 0)

    # Right Leg (Pants)
    glTranslatef(15, 0, 0)
    glColor3f(0.0, 0.0, 0.8)  # Charcoal gray pants
    gluCylinder(gluNewQuadric(), 10, 10, 50, 10, 10)

    # Left Leg (Pants)
    glTranslatef(-30, 0, 0)
    glColor3f(0.0, 0.0, 0.8)  # Charcoal gray pants
    gluCylinder(gluNewQuadric(), 10, 10, 50, 10, 10)

    # Body (Shirt)
    glTranslatef(15, 0, 50 + 20)
    glColor3f(0.2, 0.0, 0.0)   # Dark red shirt
    glutSolidCube(40)

    # Head
    glTranslatef(0, 0, 40)
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 20, 10, 10)

    # Left Arm
    glTranslatef(20, 0, -30)
    glRotatef(90, 1, 0, 0)
    glPushMatrix()
    glRotatef(left_arm_angle, 0, 1, 0)
    glColor3f(254 / 255, 223 / 255, 188 / 255)
    gluCylinder(gluNewQuadric(), 8, 8, 65, 10, 10)
    glPopMatrix()

    # Right Arm
    glRotatef(90, 1, 0, 0)
    glTranslatef(-40, 0, 0)
    glRotatef(-90 + right_arm_angle, 1, 0, 0)
    glColor3f(254 / 255, 223 / 255, 188 / 255)
    gluCylinder(gluNewQuadric(), 8, 8, 65, 10, 10)

    glPopMatrix()




def light_attack():
    global is_light_attacking, right_arm_angle
    
    if not mode_over and not is_light_attacking:
        is_light_attacking = True
        right_arm_angle = 0
        
def convert_angle_to_radians(angle):
    radian = math.radians(angle)
    cos_value = math.cos(radian)
    sin_value = math.sin(radian)
    return radian, cos_value, sin_value

def draw_bullet(bullet):
    glPushMatrix()
    glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2] + 55)
    glRotatef(90, 1, 0, 0)  # Rotate around z-axis
    glColor3f(0, 0, 0)
    glutSolidCube(5)
    glPopMatrix()

def fire_bullet():
    bullet_speed = 5
    e_bullet = {'pos': [player_pos[0]-20, player_pos[1]-5, player_pos[2]], 'angle': player_angle-90, 'speed': bullet_speed}
    bullets_list.append(e_bullet)
    
def move_bullet():
    global bullets_list, bullets_missed
    new_bullets = []
    for i in bullets_list:
        # =====================Update bullet position based on its speed and angle==============================
        val = convert_angle_to_radians(i['angle'])  
        i['pos'][0] += i['speed'] * val[1]
        i['pos'][1] += i['speed'] * val[2]
        

        new_bullets.append(i)
            
    bullets_list = new_bullets
# def strong_attack():
#     global is_strong_attacking, left_arm_angle
    
#     if not mode_over and not is_strong_attacking:
#         is_strong_attacking = True
#         left_arm_angle = 0

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

     # === Left Arm ===
    glPushMatrix()
    glColor3f(0.5, 0.2, 0.2)
    glTranslatef(20, 0, 45)  # Side of body
    glRotatef(-90, 1, 0, 0)  # Pointing forward like player
    gluCylinder(gluNewQuadric(), 4, 4, 25, 10, 10)
    glPopMatrix()

    # === Right Arm ===
    glPushMatrix()
    glColor3f(0.5, 0.2, 0.2)
    glTranslatef(-20, 0, 45)  # Side of body
    glRotatef(-90, 1, 0, 0)  # Same rotation
    gluCylinder(gluNewQuadric(), 4, 4, 25, 10, 10)
    glPopMatrix()


    glPopMatrix()

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
        glColor3f(0.5, 0.0, 0.0)  # Crimson
        gluCylinder(quad, 8, 8, 65, 10, 10)

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

        # === RIGHT ARM (close to shoulder like player) ===
        glPushMatrix()
        glTranslatef(-20, 0, 80)  # Move closer to body
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.5, 0.0, 0.0)
        gluCylinder(quad, 8, 8, 65, 10, 10)

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


def spawn_enemy(num=enemy_count):
    global enemy_list
    margin = 100  # Safety margin from arena edges
    safe_distance_from_player = 200
    safe_distance_from_boss = 150
    min_distance_between_enemies = 100

    max_attempts = 1000
    attempts = 0

    while len(enemy_list) < num and attempts < max_attempts:
        x = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
        y = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)

        too_close = False

        # Check distance from player
        dx = x - player_pos[0]
        dy = y - player_pos[1]
        dist_to_player = math.hypot(dx, dy)
        if dist_to_player < safe_distance_from_player:
            too_close = True

        # Check distance from boss if boss is spawned
        if boss_spawned:
            bx, by, _ = boss_position
            dx_boss = x - bx
            dy_boss = y - by
            dist_to_boss = math.hypot(dx_boss, dy_boss)
            if dist_to_boss < safe_distance_from_boss:
                too_close = True

        # Check distance from other enemies
        for ex, ey, _ in enemy_list:
            if math.hypot(x - ex, y - ey) < min_distance_between_enemies:
                too_close = True
                break

        if not too_close:
            enemy_list.append([x, y, 0])

        attempts += 1





def spawn_boss():
    global boss_spawned, boss_position, boss_angle

    min_distance = 300
    max_distance = 400
    distance = random.randint(min_distance, max_distance)

    angle_rad = math.radians(player_angle)

    # Spawn in the direction player is facing
    dx = -math.sin(angle_rad) * distance
    dy = -math.cos(angle_rad) * distance

    x = player_pos[0] + dx
    y = player_pos[1] + dy

    # Clamp within arena
    x = max(-GRID_LENGTH + 150, min(GRID_LENGTH - 150, x))
    y = max(-GRID_LENGTH + 150, min(GRID_LENGTH - 150, y))

    boss_position = [x, y, 0]

    # Boss should face the player → angle from boss to player
    boss_angle = (math.degrees(math.atan2(player_pos[1] - y, player_pos[0] - x)) + 90) % 360

    boss_spawned = True










                   
def mouse_listener(button, state, x, y):
    global mode_over, mode_first_person, player_turn_speed, mode_cheat_vision
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        light_attack()
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # strong_attack()
        fire_bullet()
    
def keyboard_listener(key, a, b):
    global player_angle, player_speed, player_turn_speed, player_pos, gun_angle, gun_bullet_speed, gun_bullets, gun_missed_bullets
    global mode_over, player_life, player_score, enemy_list, mode_cheat, mode_cheat_vision, mode_first_person, enemy_size
    
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
    
    player_pos = [x, y, z]
    
def specialKeyListener(key, a, b):
    global camera_angle, camera_radius, camera_height
    
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

def show_screen():
    global mode_over, player_life, player_score, gun_missed_bullets
    global boss_spawned, boss_position  # <-- Add this line

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setup_camera()
    draw_arena()
    draw_player()
    
    if not mode_over:
        for enemy in enemy_list:
            draw_enemy(*enemy)
    
    for bullet in bullets_list:
        draw_bullet(bullet)
    if boss_spawned:
        draw_boss(*boss_position)

  
    glutSwapBuffers()


def idle():
    global right_arm_angle, is_light_attacking, left_arm_angle, is_strong_attacking
 
    if is_light_attacking:
        right_arm_angle -= light_attack_speed
        if abs(right_arm_angle) >= 360:
            right_arm_angle = 0
            is_light_attacking = False
    
    
        # left_arm_angle -= strong_attack_speed
        # if abs(left_arm_angle) >= 360:
        #     left_arm_angle = 0
        #     is_strong_attacking = False
    move_bullet()
    
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy 3D")
    glEnable(GL_DEPTH_TEST)
    
    spawn_enemy(5)
    spawn_boss()  
    
    glutDisplayFunc(show_screen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouse_listener)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
