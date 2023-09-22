import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from .pygame_tools import *
import math
import numpy as np
import pygame

class UVFScreen:
    def __init__(self, world, index_uvf_robot = 2, arrow_step = 0.04):
        self.world = world
        self.index_uvf_robot = index_uvf_robot
        self.arrow_step = int(arrow_step*M_TO_PIXEL)
        self.arrow_poses = self.arrowPoses(arrow_step*M_TO_PIXEL)

    def arrowPoses(self, arrow_step):
        x = np.arange(-FIELD_DIMENSIONS[0]/2, FIELD_DIMENSIONS[0]/2, arrow_step)
        y = np.arange(-FIELD_DIMENSIONS[1]/2, FIELD_DIMENSIONS[1]/2, arrow_step)
        X,Y = np.meshgrid(x, y)
        XY = np.array([X.flatten(), Y.flatten()]).T

        return XY

    def initialiazeScreen(self):
        pygame.init()

        self.screen =  pygame.display.set_mode(FIELD_DIMENSIONS)
    
    def initialiazeObjects(self):
        #cria shapes para poder perceber que a rotação está acontecendo
        self.robotCollor = {0: (100,0,0),
                            1: (0,100,0),
                            2: (0,0,100)}
        
        self.createRobotsSurface()
        self.createUVFSurface()

    def clearScreen(self):
        #clear screen at the start of every frame
        self.screen.fill((40, 40, 40))

    def createRobotsSurface(self):
        self.robots_surf = []
        
        for index, robot in enumerate(self.world.raw_team):
            if index == MAX_ROBOTS_NUMBER:
                break

            #create new surface with white BG
            self.robots_surf.append(pygame.Surface(ROBOT_DIMENSIONS))
            self.robots_surf[index].fill((255,255,255))

            #set a color key for blitting
            self.robots_surf[index].set_colorkey((255, 0, 255))

            #create shapes so you can tell rotation is happenning
            robotMask1 =  pygame.Rect(ROBOT_DIMENSIONS[1]*2/3, ROBOT_DIMENSIONS[1]/3, 2.5*CM_TO_PIXEL, 2.5*CM_TO_PIXEL)
            robotMask2 =  pygame.Rect(0, ROBOT_DIMENSIONS[1]*0.4375, int(7.5*CM_TO_PIXEL), int(0.75*CM_TO_PIXEL))

            #draw the shape to that surface
            pygame.draw.rect(self.robots_surf[index], self.robotCollor[index], robotMask1)
            pygame.draw.rect(self.robots_surf[index], self.robotCollor[index], robotMask2)

            #draw surf to screen and catch the rect that blit returns
            blittedRect = self.screen.blit(self.robots_surf[index], centralField2pygameAxisCoordinate((robot.x,robot.y)))
    
    def drawRobots(self):
        for index, robot in enumerate(self.world.raw_team):
            if index == MAX_ROBOTS_NUMBER:
                break

            #rotate surf by DEGREE amount degrees
            rotatedSurf =  pygame.transform.rotate(self.robots_surf[index], math.degrees(robot.th))

            #get the rect of the rotated surf and set it's center to the oldCenter
            rotRect = rotatedSurf.get_rect()
            rotRect.center = centralField2pygameAxisCoordinate((robot.x*M_TO_PIXEL,robot.y*M_TO_PIXEL))

            #draw rotatedSurf with the corrected rect so it gets put in the proper spot
            self.screen.blit(rotatedSurf, rotRect)


    def drawBall(self):
        pygame.draw.circle(self.screen, (100, 0, 0), centralField2pygameAxisCoordinate((self.world.ball.x*M_TO_PIXEL, self.world.ball.y*M_TO_PIXEL)), BALL_RADIUS)

    def createUVFSurface(self):
        # self.arrows_surf = pygame.Surface((self.arrow_step, self.arrow_step))
        # self.arrows_surf.fill((40,40,40))
        # self.arrows_surf.set_colorkey((255, 255, 255))

        # #create shapes so you can tell rotation is happenning
        # robotMask =  pygame.Rect(ROBOT_DIMENSIONS[1]*2/3, ROBOT_DIMENSIONS[1]/3, 2.5*CM_TO_PIXEL, 2.5*CM_TO_PIXEL)

        # #draw the shape to that surface
        # # pygame.draw.rect(self.arrows_surf[index], (255,255,255), robotMask)
        # pygame.draw.line(self.arrows_surf, (255,255,255), (0, self.arrow_step/2), (self.arrow_step-4, self.arrow_step/2))
        # pygame.draw.circle(self.arrows_surf, (255,255,255), (int(self.arrow_step-4), int(self.arrow_step/2)), int(0.5*CM_TO_PIXEL))

        # # #draw surf to screen and catch the rect that blit returns
        # blittedRect = self.screen.blit(self.arrows_surf, centralField2pygameAxisCoordinate((0,0)))

        self.arrows_surf = []
        
        robot = self.world.raw_team[self.index_uvf_robot]

        for index in range(self.arrow_poses.shape[0]):
            #create new surface with white BG
            self.arrows_surf.append(pygame.Surface((self.arrow_step, self.arrow_step)))
            self.arrows_surf[index].fill((40,40,40))

            # #set a color key for blitting
            # self.arrows_surf[index].set_colorkey((255, 255, 255))

            #draw the shape to that surface
            # pygame.draw.rect(self.arrows_surf[index], (255,255,255), robotMask)
            pygame.draw.line(self.arrows_surf[index], (255,255,255), (0, self.arrow_step/2), (self.arrow_step-4, self.arrow_step/2))
            pygame.draw.circle(self.arrows_surf[index], (255,255,255), (int(self.arrow_step-4), int(self.arrow_step/2)), int(0.5*CM_TO_PIXEL))

            # #draw surf to screen and catch the rect that blit returns
            blittedRect = self.screen.blit(self.arrows_surf[index], centralField2pygameAxisCoordinate(self.arrow_poses[index]))


    def drawUVF(self):
        robot = self.world.raw_team[self.index_uvf_robot]

        if robot.field is None: 
            return

        for index in range(self.arrow_poses.shape[0]):
            #rotate surf by DEGREE amount degrees
            th = robot.field.F(self.arrow_poses[index]/M_TO_PIXEL)
            rotatedSurf =  pygame.transform.rotate(self.arrows_surf[index], math.degrees(th))

            #get the rect of the rotated surf and set it's center to the oldCenter
            rotRect = rotatedSurf.get_rect()
            rotRect.center = centralField2pygameAxisCoordinate(self.arrow_poses[index])

            #draw rotatedSurf with the corrected rect so it gets put in the proper spot
            self.screen.blit(rotatedSurf, rotRect)

        
    def updateScreen(self):        
        self.clearScreen()

        self.drawUVF()
        self.drawRobots()
        self.drawBall()

        #show the screen surface
        pygame.display.flip()