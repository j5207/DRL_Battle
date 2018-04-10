import numpy as np
import os
import pygame
import time
import random
import uuid
import sys
from pygame.locals import *
from main import *
from constant import *
from field_map import *

class Game:
    def __init__(self):
        self.tile_size = 10
        pygame.init()
        self.screen = pygame.display.set_mode((500 + 2 * self.tile_size, 800 + 2 * self.tile_size))
        self.clock = pygame.time.Clock()
        self.m = RoboMasterMap()
        self.m.draw_rect1(self.tile_size, self.screen)
        Bonus()
    
        self.tankgroup = pygame.sprite.Group()
        self.bulletgroup = pygame.sprite.Group()
        self.allgroup = pygame.sprite.LayeredUpdates()
    
        Tank._layer = 4   # base layer
        Bullet._layer = 7 # to prove that Bullet is in top-layer
        Turret._layer = 6 # above Tank & Tracer
        Text._layer = 3   # below Tank
    
        #assign default groups to each sprite class
        Tank.groups = self.tankgroup, self.allgroup
        # Tank.groups = self.tankgroup, self.allgroup
        Turret.groups = self.allgroup
        Bullet.groups = self.bulletgroup, self.allgroup
        Text.groups = self.allgroup
        self.player1 = Tank((420,720), 90)
        self.ai1 = Tank((80,80), -90,False)
        self.ai2 = Tank((120,80), -90,False)
        self.terminal = False
        Bonus()
        milliseconds = self.clock.tick(100)  # milliseconds passed since last frame
        self.seconds = milliseconds / 1000.0 # seconds passed since last frame (float)

    def frame_step(self, action):
        pygame.event.pump()                 
        self.m.draw_rect(self.tile_size, self.screen)
        self.allgroup.update(action, self.seconds)
        reward, observation, terminal = self.player1.get_return()
        self.allgroup.draw(self.screen)
        #print(reward, observation, terminal)
        pygame.display.update() # flip the screen 30 times a second

        return reward, observation, terminal

    def reset(self):
        self.player1.reset()
        self.ai1.reset()
        self.ai2.reset()


# if __name__ == "__main__":
#     t = Game() 
#     t.frame_step()
