import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

class Visualiser:

    def main_init(self):
        video_flags = OPENGL | DOUBLEBUF
        pygame.init()
        screen = pygame.display.set_mode((640, 480), video_flags)
        pygame.display.set_caption("Press Esc to quit")
        self.resize(640, 480)
        self.init()

    def resize(self, width, height):  
        if height == 0: 
            height = 1  
        glViewport(0, 0, width, height) 
        glMatrixMode(GL_PROJECTION) 
        glLoadIdentity()    
        gluPerspective(45, 1.0 * width / height, 0.1, 100.0)    
        glMatrixMode(GL_MODELVIEW)  
        glLoadIdentity()    

    def init(self): 
        glShadeModel(GL_SMOOTH) 
        glClearColor(0.0, 0.0, 0.0, 0.0)    
        glClearDepth(1.0)   
        glEnable(GL_DEPTH_TEST) 
        glDepthFunc(GL_LEQUAL)  
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)   

    #Funtion to display in GUI  
    def drawtext(self, position, textstring): 
        font = pygame.font.SysFont("Courier", 18, True) 
        textsurface = font.render(textstring, True, (255, 255, 255, 255), (0, 0, 0, 255))   
        textData = pygame.image.tostring(textsurface, "RGBA", True) 
        glRasterPos3d(*position)    
        glDrawPixels(textsurface.get_width(), textsurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)    

    #Function to display the block      
    def draw(self, ax, ay, az):   
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  

        glLoadIdentity()    
        glTranslatef(0, 0.0, -7.0)  

        osd_line = f'y: {str(round(ay, 2))}, x: {str(round(ax, 2))}, z: {str(round(az, 2))}'    


        self.drawtext((-2, -2, 2), osd_line) 

        # the way I'm holding the IMU board, X and Y axis are switched,with respect to the OpenGL coordinate system 

        glRotatef(ax, 0.0, 1.0, 0.0)      # Yaw, rotate around y-axis   
        glRotatef(ay, 1.0, 0.0, 0.0)          # Pitch, rotate around x-axis 
        glRotatef(az, 0.0, 0.0, 1.0)     # Roll, rotate around z-axis  

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
