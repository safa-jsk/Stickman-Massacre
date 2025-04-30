

    # # Legs
    # glPushMatrix()
    # glColor3f(0.6, 0.1, 0.1)
    # glTranslatef(10, -10, 10)
    # gluCylinder(gluNewQuadric(), 5, 5, 20, 10, 10)
    # glTranslatef(-20, 0, 0)
    # gluCylinder(gluNewQuadric(), 5, 5, 20, 10, 10)
    # glPopMatrix()

    # # Body (with armor-like cube chest)
    # glPushMatrix()
    # glColor3f(0.9, 0.2, 0.2)  # Deep red
    # glTranslatef(0, 0, 40)
    # glScalef(1.5, 1.0, 1.5)
    # glutSolidCube(30)
    # glPopMatrix()

    # # Head (slightly forward and above body)
    # glPushMatrix()
    # glColor3f(0.1, 0.1, 0.1)  # Dark head
    # glTranslatef(0, 0, 60)
    # gluSphere(gluNewQuadric(), 10, 10, 10)
    # glPopMatrix()

    # # Eyes
    # glPushMatrix()
    # glColor3f(0, 1, 1)  # Cyan glowing eyes
    # glTranslatef(-4, 10, 63)
    # glutSolidCube(3)
    # glTranslatef(8, 0, 0)
    # glutSolidCube(3)
    # glPopMatrix()

    #  # === Left Arm ===
    # glPushMatrix()
    # glColor3f(0.5, 0.2, 0.2)
    # glTranslatef(20, 0, 45)  # Side of body
    # glRotatef(-90, 1, 0, 0)  # Pointing forward like player
    # gluCylinder(gluNewQuadric(), 4, 4, 25, 10, 10)
    # glPopMatrix()

    # # === Right Arm ===
    # glPushMatrix()
    # glColor3f(0.5, 0.2, 0.2)
    # glTranslatef(-20, 0, 45)  # Side of body
    # glRotatef(-90, 1, 0, 0)  # Same rotation
    # gluCylinder(gluNewQuadric(), 4, 4, 25, 10, 10)
    # glPopMatrix()