from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import math

#from read_data import *

from ahrs.filters import Mahony
import serial
import numpy

import math


def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x*57.2957795, pitch_y*57.2957795, yaw_z*57.2957795 # in radians


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

# def main(port, Q):
#     video_flags = OPENGL | DOUBLEBUF
#     pygame.init()
#     screen = pygame.display.set_mode((640, 480), video_flags)
#     pygame.display.set_caption("Press Esc to quit, z toggles yaw mode")
#     resize(640, 480)
#     init()
#     frames = 0
#     ticks = pygame.time.get_ticks()
    
#     while 1:
#         event = pygame.event.poll()
#         if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
#             break
#         if event.type == KEYDOWN and event.key == K_z:
#             yaw_mode = not yaw_mode
        
#         pygame.display.flip()
#         frames = frames + 1

#         gyro_data, acc_data, mag_data = process_raw_data(port.readline().decode('utf-8'))
#         Q = madgwick_obj.updateMARG(Q, gyr=gyro_data, acc=acc_data, mag=mag_data)
#         x, y, z = Quaternion_to_Euler(Q)
#         #print(x, y, z)
#         draw(x, y, z)


def main():
    port = serial.Serial('COM3', 115200)

    orientation = Mahony(frequency=5)

    quaternions = []
    gyro_data = []
    acc_data = []
    mag_data = []

    q = numpy.array([1, 0.0, 0.0, 0.0])
    quaternions.append(q)

    video_flags = OPENGL | DOUBLEBUF
    pygame.init()
    screen = pygame.display.set_mode((640, 480), video_flags)
    pygame.display.set_caption("Press Esc to quit, z toggles yaw mode")
    resize(640, 480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()

    while True:
        raw_data = port.readline()
        raw_data = raw_data.decode('utf-8').rstrip('\r\n').split(';')
        acc, gyro = raw_data

        acc = [float(i) for i in acc.split()]
        acc_data.append(acc)
        gyro = [float(i) for i in gyro.split()]
        gyro[0] += 0.04
        gyro[1] += 0.06
        gyro[2] += 0.01
        gyro_data.append(gyro)
        q = orientation.updateIMU(quaternions[-1], gyro, acc)
        w_q = q[0]
        x_q = q[1]
        y_q = q[2]
        z_q = q[3]

        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if event.type == KEYDOWN and event.key == K_z:
            yaw_mode = not yaw_mode
        
        pygame.display.flip()
        frames = frames + 1

        x, y, z = euler_from_quaternion(x_q, y_q, z_q, w_q)
        print(x, y, z)
        draw(y, x, z)
        # print(euler_from_quaternion(x, y, z, w))
        quaternions.append(q)

main()