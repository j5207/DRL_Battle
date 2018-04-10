import numpy as np
import os
import pygame
import time
import random
import uuid
import sys
from pygame.locals import *

from constant import *


class Wall(object):
    
    def __init__(self, pos):
        WALL_LIST.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], 10, 10)

class Bonus(object):
    def __init__(self):
        self.rect = pygame.Rect(221, 371, 58, 58)

class RoboMasterMap():
    (TILE_EMPTY, TILE_WALL, TILE_STARTING, TILE_GOAL, TILE_BONUS) = range(5)

    def __init__(self, tile_size=100):
        self.map_size = (8000, 5000)
        self.tile_size = tile_size
        self.tile_color = [
            (225, 225, 225),
            (0, 255, 0),
            (200, 200, 255),
            (255, 200, 200),
            (0, 0, 0),
        ]
        # make map
        self.map = np.zeros(self.map_size, dtype=int)
        self.fill_map((0, 0), (1330, 1330), self.TILE_GOAL)
        self.fill_map(
            (self.map_size[0] - 1330, self.map_size[1] - 1330), (1330, 1330), self.TILE_STARTING)
        self.fill_map(
            (np.int((self.map_size[0] - 580) / 2), np.int((self.map_size[1] - 580) / 2)), (580, 580), self.TILE_BONUS)
        self.fill_obstacle((0, 2200), (800, 300))
        self.fill_obstacle((1800, 1500), (300, 1200))
        self.fill_obstacle((1200, 3700), (800, 300))
        self.fill_obstacle((3100, 0), (300, 2000))
        # convert to pygame axis
        self.map = np.transpose(self.map)
        # generate tile map
        self.tile_map = self.make_map_tiles()
        #self.tile_map = self.map

    def fill_map(self, loc, size, tile_type):
        self.map[loc[0]:loc[0]+size[0], loc[1]:loc[1]+size[1]].fill(tile_type)

    def fill_obstacle(self, loc, size):
        self.fill_map(loc, size, self.TILE_WALL)
        self.fill_map((self.map.shape[0] - loc[0] - size[0],
                       self.map.shape[1] - loc[1] - size[1]), size, self.TILE_WALL)

    def make_map_tiles(self):
        h = int(np.floor(self.map.shape[0] / self.tile_size))
        w = int(np.floor(self.map.shape[1] / self.tile_size))
        new_map = np.zeros((h, w))
        for (x, y), tile_type in np.ndenumerate(new_map):
            new_map[x, y] = np.max(self.map[x * self.tile_size: (x + 1) *
                                            self.tile_size, y * self.tile_size: (y + 1) * self.tile_size])
        # add surrounding walll
        new_map = np.pad(new_map, (1, 1), 'constant', constant_values=(self.TILE_WALL, self.TILE_WALL))
        del self.map
        return new_map

    def draw_rect(self, rect_tile_size, screen):
        '''Draw map on screen'''
        obstacles = pygame.sprite.Group()
        for (x, y), tile_type in np.ndenumerate(self.tile_map):
            screen.subsurface(x * rect_tile_size, y * rect_tile_size,
                              rect_tile_size, rect_tile_size).fill(self.tile_color[int(tile_type)])
        pygame.display.update()

    def draw_rect1(self, rect_tile_size, screen):
        '''Draw map on screen'''
        obstacles = pygame.sprite.Group()
        for (x, y), tile_type in np.ndenumerate(self.tile_map):
            screen.subsurface(x * rect_tile_size, y * rect_tile_size,
                              rect_tile_size, rect_tile_size).fill(self.tile_color[int(tile_type)])
            if tile_type == 1:
                Wall((x * rect_tile_size, y * rect_tile_size))
        pygame.display.update()





# if __name__ == "__main__":
#     tile_size = 10
#     pygame.init()
#     screen = pygame.display.set_mode((500 + 2 * tile_size, 800 + 2 * tile_size))
#     pygame.display.set_caption("My Game")
#     clock = pygame.time.Clock()
#     m = RoboMasterMap()
#     m.draw_rect1(tile_size, screen)
#     t = Tank(tile_size)
#     Bonus()
#     done = False
#     while done == False:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 done = True
#             if event.type == KEYDOWN:
#                 if event.key == K_LEFT:
#                     pass
#         clock.tick(100)
#         m.draw_rect(tile_size, screen)
#         pressed_keys = pygame.key.get_pressed()
#         t.move(pressed_keys, screen)
#         tank_position , tank_angle= t.get_tank_pos()
#         Bullet(tank_position, tank_angle, screen)

#         BUFF = t.update_buff(BUFF)
#         #print(BUFF)







    pygame.quit()
