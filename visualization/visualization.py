from analyser import Analyzer
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import math
import pandas as pd
import time
import numpy as np


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
def draw(ax, ay, az, screen, i, str_condition):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    # osd_text = "pitch: " + str("{0:.2f}".format(ay)) + ", roll: " + str("{0:.2f}".format(ax))

    # if yaw_mode:
    #     osd_line = osd_text + ", yaw: " + str("{0:.2f}".format(az))
    # else:
    #     osd_line = osd_text

    drawtext((-2.7, -1.5, 2), str_condition)

    # the way I'm holding the IMU board, X and Y axis are switched,with respect to the OpenGL coordinate system
    
    # if yaw_mode:  
    #     az=az+180  #Comment out if reading Euler Angle/Quaternion angles 
    #     glRotatef(az, 0.0, 1.0, 0.0)      # Yaw, rotate around y-axis

 
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

def read_data(path):
    #data frame from rounded data file
    df = pd.read_csv(path)
    rounded = np.round(df)

    #find optimal and delete it from data frame
    optimal = df.tail(1)
    x1_optimal = optimal['x1'].tolist()[0]
    y1_optimal = optimal['y1'].tolist()[0]
    x2_optimal = optimal['x2'].tolist()[0]
    y2_optimal = optimal['y2'].tolist()[0]
    df = df.head(-1)

    #find all par for graphs
    time = df['computer_time'].tolist()
    start_time = time[0]
    time = [i-start_time for i in time]
    x1 = df['x1'].tolist()
    x1 = [i+x1_optimal for i in x1]
    y1 = df['y1'].tolist()
    y1 = [i-y1_optimal for i in y1]

    x2 = df['x2'].tolist()
    x2 = [i+x2_optimal for i in x2]
    y2 = df['y2'].tolist()
    y2 = [i-y2_optimal for i in y2]
    return x1, y1, x2, y2

# def main(port, Q):
def main(path=None):
    analyser = Analyzer()
    video_flags = OPENGL | DOUBLEBUF
    pygame.init()
    screen = pygame.display.set_mode((640, 480), video_flags)
    pygame.display.set_caption("Press Esc to quit, z toggles yaw mode")
    resize(640, 480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()
    if path:
        x1, y1, x2, y2 = read_data(path)
        for i in range(len(x1)):
            event = pygame.event.poll()
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                break
            if event.type == KEYDOWN and event.key == K_z:
                yaw_mode = not yaw_mode

            pygame.display.flip()
            frames = frames + 1

            # gyro_data, acc_data, mag_data = process_raw_data(port.readline().decode('utf-8'))
            # Q = madgwick_obj.updateMARG(Q, gyr=gyro_data, acc=acc_data, mag=mag_data)
            # x, y, z = Quaternion_to_Euler(Q)
            #print(x, y, z)
            x, y = x1[i], y1[i]
            str_condition = analyser.check_mode((x, y), (x2[i], y2[i]))
            draw(x, y, 0, screen, i, str_condition)
            time.sleep(0.1)
    
    print(f'Thanks for usage, overall result is {analyser.info_on_user}')

if __name__ == '__main__':
    path = 'datasets/angles/angles_forward_rotations.csv'
    main(path)
