from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import math

from read_data import *

yaw_mode = False

def resize(width, height):
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0 * width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

#Funtion to display in GUI 
def drawtext(position, textstring):
    font = pygame.font.SysFont("Courier", 18, True)
    textsurface = font.render(textstring, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textsurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textsurface.get_width(), textsurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

#Function to display the block  
def draw(ax, ay, az):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    osd_text = "pitch: " + str("{0:.2f}".format(ay)) + ", roll: " + str("{0:.2f}".format(ax))

    if yaw_mode:
        osd_line = osd_text + ", yaw: " + str("{0:.2f}".format(az))
    else:
        osd_line = osd_text

    drawtext((-2, -2, 2), osd_line)

    # the way I'm holding the IMU board, X and Y axis are switched,with respect to the OpenGL coordinate system
    
    if yaw_mode:  
        az=az+180  #Comment out if reading Euler Angle/Quaternion angles 
        glRotatef(az, 0.0, 1.0, 0.0)      # Yaw, rotate around y-axis

 
    glRotatef(ay, 1.0, 0.0, 0.0)          # Pitch, rotate around x-axis
    glRotatef(-1 * ax, 0.0, 0.0, 1.0)     # Roll, rotate around z-axis

    glBegin(GL_QUADS)
    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(1.0, 0.2, 1.0)

    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(1.0, -0.2, -1.0)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, -1.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, 1.0)

    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, -1.0)
    glEnd()

#This function reads the Quaternion angle readings from the BnO055
def Quaternion_to_Euler(Q):
        #Turns the Quaternion readings into Euler Angles for projection
        w, x, y, z = Q[0], Q[1], Q[2], Q[3]
        ysqr = y*y
        t0 = +2.0 * (w * x + y*z)
        t1 = +1.0 - 2.0 * (x*x + ysqr)
        ax = (math.degrees(math.atan2(t0, t1)))
        
        t2 = +2.0 * (w*y - z*x)
        t2 =  1 if t2 > 1 else t2
        t2 = -1 if t2 < -1 else t2
        ay= math.degrees(math.asin(t2))
       
        t3 = +2.0 * (w * z + x*y)
        t4 = +1.0 - 2.0 * (ysqr + z*z)
        az=math.degrees(math.atan2(t3, t4))
        return ax, ay, az

def main(port, Q):
    video_flags = OPENGL | DOUBLEBUF
    pygame.init()
    screen = pygame.display.set_mode((640, 480), video_flags)
    pygame.display.set_caption("Press Esc to quit, z toggles yaw mode")
    resize(640, 480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()
    
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if event.type == KEYDOWN and event.key == K_z:
            yaw_mode = not yaw_mode
        
        pygame.display.flip()
        frames = frames + 1

        gyro_data, acc_data, mag_data = process_raw_data(port.readline().decode('utf-8'))
        Q = madgwick_obj.updateMARG(Q, gyr=gyro_data, acc=acc_data, mag=mag_data)
        x, y, z = Quaternion_to_Euler(Q)
        #print(x, y, z)
        draw(x, y, z)
