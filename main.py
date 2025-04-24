from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

import math
import random

# System Congiguration
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_LENGTH = 600
fovY = 120

# Camera-related variables
camera_pos = [0, 600, 600]
camera_angle = 0
camera_radius = 200
camera_height = 200

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

def draw_grid():
    glBegin(GL_QUADS)
    
    for i in range(-GRID_LENGTH, GRID_LENGTH + 1, 100):
        for j in range(-GRID_LENGTH, GRID_LENGTH + 1, 100):
            if (i + j) % 200 == 0:
                glColor3f(32/255, 97/255, 33/255)  # Dark Green
            else:
                glColor3f(63/255, 192/255, 65/255)  # Light Green        
            
            glVertex3f(i, j, 0)                 # Bottom left
            glVertex3f(i + 100, j, 0)           # Bottom right
            glVertex3f(i + 100, j + 100, 0)     # Top right
            glVertex3f(i, j + 100, 0)           # Top left

    # Boundary walls
    glColor3f(129/255, 255/255, 129/255)  # Light Green
    
    # Left Wall
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)           # Bottom left
    glVertex3f(-GRID_LENGTH, GRID_LENGTH+100, 0)        # Top left
    glVertex3f(-GRID_LENGTH, GRID_LENGTH+100, 100)      # Top right
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 100)         # Bottom right
    
    # Right Wall
    glVertex3f(GRID_LENGTH+100, -GRID_LENGTH, 0)        # Bottom left
    glVertex3f(GRID_LENGTH+100, GRID_LENGTH+100, 0)     # Top left
    glVertex3f(GRID_LENGTH+100, GRID_LENGTH+100, 100)   # Top right
    glVertex3f(GRID_LENGTH+100, -GRID_LENGTH, 100)      # Bottom right
    
    # Bottom Wall
    glVertex3f(-GRID_LENGTH, GRID_LENGTH+100, 0)        # Bottom left
    glVertex3f(GRID_LENGTH+100, GRID_LENGTH+100, 0)     # Top left
    glVertex3f(GRID_LENGTH+100, GRID_LENGTH+100, 100)   # Top right
    glVertex3f(-GRID_LENGTH, GRID_LENGTH+100, 100)      # Bottom right
    
    # Top Wall
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)           # Bottom left
    glVertex3f(GRID_LENGTH+100, -GRID_LENGTH, 0)        # Top left
    glVertex3f(GRID_LENGTH+100, -GRID_LENGTH, 100)      # Top right
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 100)         # Bottom right
    
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
    
    if mode_over:
        glRotatef(-90, 1, 0, 0)
    
    # Right Leg
    glTranslatef(15, 0, 0)      # At (15, 0, 0)
    glColor3f(0.0, 0.0, 1.0)
    gluCylinder(gluNewQuadric(), 10, 10, 50, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    # Left Leg
    glTranslatef(-30, 0, 0)     # At (-15, 0, 0)
    glColor3f(0.0, 0.0, 1.0)
    gluCylinder(gluNewQuadric(), 10, 10, 50, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    # Body
    glTranslatef(15, 0, 50+20)  # At (0, 0, 70)
    glColor3f(85/255, 108/255, 47/255)
    glutSolidCube(40)
    
    # Head
    glTranslatef(0, 0, 40)      # At (15, 0, 110)
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 20, 10, 10) # radius, slices, stacks
    
    # Left Arm
    glTranslatef(20, 0, -30)   # At (35, -60, 80)
    glRotatef(90, 1, 0, 0)
    
    glPushMatrix()
    glRotatef(left_arm_angle, 0, 1, 0)  # Apply attack rotation
    glColor3f(254/255, 223/255, 188/255)
    gluCylinder(gluNewQuadric(), 8, 8, 65, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    glPopMatrix()
    
    # Right Arm
    glRotatef(90, 1, 0, 0)      # Reset rotation
    glTranslatef(-40, 0, 0)     # At (-5, -60, 80)
    glRotatef(-90 + right_arm_angle, 1, 0, 0)  # Apply attack rotation    
    glColor3f(254/255, 223/255, 188/255)
    gluCylinder(gluNewQuadric(), 8, 8, 65, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    glPopMatrix()

def light_attack():
    global is_light_attacking, right_arm_angle
    
    if not mode_over and not is_light_attacking:
        is_light_attacking = True
        right_arm_angle = 0
        
def strong_attack():
    global is_strong_attacking, left_arm_angle
    
    if not mode_over and not is_strong_attacking:
        is_strong_attacking = True
        left_arm_angle = 0

def draw_enemy(x, y, z):
    glPushMatrix()
    
    # Position and orientation
    glTranslatef(x, y, z)  # Enemy position
    glColor3f(1.0, 0.0, 0.0)

    # Enemy half the size of the player
    
    # Right Leg
    glTranslatef(10, 0, 0)      # At (10, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 5, 40, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    # Left Leg
    glTranslatef(-20, 0, 0)     # At (-10, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 5, 40, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    # Body
    glTranslatef(10, 0, 25+10)  # At (0, 0, 35)
    gluCylinder(gluNewQuadric(), 10, 10, 30, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    # Head
    glTranslatef(0, 0, 35)      # At (0, 0, 70)
    gluSphere(gluNewQuadric(), 10, 10, 10) # radius, slices, stacks
    
    # Left Arm
    glTranslatef(10, 0, -15)   # At (10, 0, 40)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 4, 4, 20, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    # Right Arm
    glRotatef(-90, 0, 1, 0)      # Reset rotation
    glTranslatef(-20, 0, 0)     # At (-10, 0, 40)
    glRotatef(-90, 0, 1, 0)     # Rotate back to original position
    gluCylinder(gluNewQuadric(), 4, 4, 20, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    glPopMatrix()

def spawn_enemy(num = enemy_count):
    global enemy_list, enemy_size, enemy_speed
    
    for i in range(num):
        x = random.uniform(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        y = random.uniform(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        z = 0
        while abs(x) < player_pos[0] + 200:
            x = random.uniform(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        while abs(y) < player_pos[1] + 200:
            y = random.uniform(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        enemy_list.append([x, y, z])
                   
def mouse_listener(button, state, x, y):
    global mode_over, mode_first_person, player_turn_speed, mode_cheat_vision
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        light_attack()
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        strong_attack()
    
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
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setup_camera()
    draw_grid()
    draw_player()
    
    if not mode_over:
        for enemy in enemy_list:
            draw_enemy(*enemy)
    
    glutSwapBuffers()

def idle():
    global right_arm_angle, is_light_attacking, left_arm_angle, is_strong_attacking
    
    if is_light_attacking:
        right_arm_angle -= light_attack_speed
        if abs(right_arm_angle) >= 360:
            right_arm_angle = 0
            is_light_attacking = False
    
    if is_strong_attacking:
        left_arm_angle -= strong_attack_speed
        if abs(left_arm_angle) >= 360:
            left_arm_angle = 0
            is_strong_attacking = False
    
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy 3D")
    glEnable(GL_DEPTH_TEST)
    
    spawn_enemy()
    
    glutDisplayFunc(show_screen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouse_listener)
    
    glutMainLoop()

if __name__ == "__main__":
    main()