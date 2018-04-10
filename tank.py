import pygame
import math
from pygame.locals import *
from constant import *
from random import randint

class Wall(object):
    
    def __init__(self, pos):
        walls.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], 10, 10)


class Tank(pygame.sprite.Sprite):
    def __init__(self, tile_size):
        super(Tank, self).__init__()
        self.my_tank = pygame.transform.scale(pygame.image.load("images/tankgreen1.png"), (TANK_WID, TANK_HEI))
        self.my_tank_clean = self.my_tank.copy()
        self.position = self.my_tank.get_rect()
        self.position[0] = tile_size
        self.position[1] = tile_size
        self.tile_size = tile_size
        self.angle_offset = 90
        self.angle = 0
        self.HP = 2000
        self.alive = True
        self.team = 0
    
    
    def rot_center(self, image, rect, angle):
        """rotate an image while keeping its center and size"""
        self.rot_image = pygame.transform.rotate(image, angle)
        self.rot_rect = self.rot_image.get_rect(center=rect.center)
        return self.rot_image, self.rot_rect


    def move(self, pressed_keys, screen):
        '''Move Robot Using Keyboard'''
        #global enemies
        sin = math.sin(math.radians(self.angle-self.angle_offset))
        cos = math.cos(math.radians(self.angle-self.angle_offset))
        #print(self.angle)
        
        if pressed_keys[K_w] and self.position.move(round(sin*F_VELOCITY), round(cos*F_VELOCITY)).collidelist(walls) == -1:
            self.position.move_ip(round(sin*F_VELOCITY), round(cos*F_VELOCITY))
        elif pressed_keys[K_x] and self.position.move(round(-sin*F_VELOCITY), round(-cos*F_VELOCITY)).collidelist(walls) == -1:
            self.position.move_ip(round(-sin*F_VELOCITY), round(-cos*F_VELOCITY))
        elif pressed_keys[K_a] and self.position.move(round(cos*S_VELOCITY), round(-sin*S_VELOCITY)).collidelist(walls) == -1:
            self.position.move_ip(round(cos*S_VELOCITY), round(-sin*S_VELOCITY))
        elif pressed_keys[K_d] and self.position.move(round(-cos*S_VELOCITY), round(sin*S_VELOCITY)).collidelist(walls) == -1:
            self.position.move_ip(round(-cos*S_VELOCITY), round(sin*S_VELOCITY))
        
        elif pressed_keys[K_q] and self.position.move(round((sin*F_VELOCITY+cos*S_VELOCITY)/2), round((cos*F_VELOCITY-sin*S_VELOCITY)/2)).collidelist(walls) == -1:
            #print((cos*F_VELOCITY-sin*S_VELOCITY)/2)
            self.position.move_ip(round((sin*F_VELOCITY+cos*S_VELOCITY)/2), round((cos*F_VELOCITY-sin*S_VELOCITY)/2))
        elif pressed_keys[K_e] and self.position.move(round((sin*F_VELOCITY-cos*S_VELOCITY)/2),round((cos*F_VELOCITY+sin*S_VELOCITY)/2)).collidelist(walls) == -1:
            #print((cos*F_VELOCITY+sin*S_VELOCITY)/2)
            self.position.move_ip(round((sin*F_VELOCITY-cos*S_VELOCITY)/2), round((cos*F_VELOCITY+sin*S_VELOCITY)/2))
        elif pressed_keys[K_z] and self.position.move(round((-sin*F_VELOCITY+cos*S_VELOCITY)/2), round((-cos*F_VELOCITY-sin*S_VELOCITY)/2)).collidelist(walls) == -1:
            self.position.move_ip(round((-sin*F_VELOCITY+cos*S_VELOCITY)/2), round((-cos*F_VELOCITY-sin*S_VELOCITY)/2))
        elif pressed_keys[K_c] and self.position.move(round((-sin*F_VELOCITY-cos*S_VELOCITY)/2), round((-cos*F_VELOCITY+sin*S_VELOCITY)/2)).collidelist(walls) == -1:
            self.position.move_ip(round((-sin*F_VELOCITY-cos*S_VELOCITY)/2), round((-cos*F_VELOCITY+sin*S_VELOCITY)/2))
        
        elif pressed_keys[K_j] and self.rot_center(self.my_tank_clean, self.position, self.angle+30)[1].collidelist(walls) == -1:
            self.angle += 30
            self.angle = self.angle % 360
            self.my_tank , self.position= self.rot_center(self.my_tank_clean, self.position, self.angle)
        elif pressed_keys[K_l] and self.rot_center(self.my_tank_clean, self.position, self.angle-30)[1].collidelist(walls) == -1:
            self.angle -= 30
            self.angle = self.angle % 360
            self.my_tank , self.position= self.rot_center(self.my_tank_clean, self.position, self.angle)
        
        screen.blit(self.my_tank, self.position)



class AITank(pygame.sprite.Sprite):
    def __init__(self, tile_size, serial_number):
        super(AITank, self).__init__()
        self.my_tank = pygame.transform.scale(pygame.image.load("images/tankpurple1.png"), (TANK_WID, TANK_HEI))
        self.my_tank_clean = self.my_tank.copy()
        self.position = self.my_tank.get_rect()
        
        self.position[0] = 420
        self.position[1] = 750 - serial_number * TANK_HEI
        self.tile_size = tile_size
        self.angle_offset = 90
        self.angle = 0
        self.HP = 2000
        self.team = 1
        self.alive = True
        self.buff = False
        self.dir = 0
    def rot_center(self, image, rect, angle):
        """rotate an image while keeping its center and size"""
        self.rot_image = pygame.transform.rotate(image, angle)
        self.rot_rect = self.rot_image.get_rect(center=rect.center)
        return self.rot_image, self.rot_rect
    
    
    def move(self, screen):
        sin = math.sin(math.radians(self.angle-self.angle_offset))
        cos = math.cos(math.radians(self.angle-self.angle_offset))
        #print(self.position)
        '''Move Robot to the center of the stage'''
        if self.buff == False:
            if self.angle < 270 and self.angle > 90 and self.rot_center(self.my_tank_clean, self.position, self.angle+30)[1].collidelist(walls) == -1:
                self.angle += 30
                self.angle = self.angle % 360
                self.my_tank , self.position= self.rot_center(self.my_tank_clean, self.position, self.angle)
            elif (self.angle > 270 or self.angle < 90) and self.rot_center(self.my_tank_clean, self.position, self.angle-30)[1].collidelist(walls) == -1:
                self.angle -= 30
                self.angle = self.angle % 360
                self.my_tank , self.position= self.rot_center(self.my_tank_clean, self.position, self.angle)
            elif self.position[1] >= 420 and self.position.move(round(sin*F_VELOCITY), round(cos*F_VELOCITY)).collidelist(walls) == -1:
                self.position.move_ip(round(sin*F_VELOCITY), round(cos*F_VELOCITY))
                self.dir = 0
            elif self.position[0] <= 220 and self.position.move(round(-cos*S_VELOCITY), round(sin*S_VELOCITY)).collidelist(walls) == -1:
                self.position.move_ip(round(-cos*S_VELOCITY), round(sin*S_VELOCITY))
                self.dir = 0
            elif self.position[0] >= 250 and self.position.move(round(cos*S_VELOCITY), round(-sin*S_VELOCITY)).collidelist(walls) == -1:
                self.position.move_ip(round(cos*S_VELOCITY), round(-sin*S_VELOCITY))
                self.dir = 0
            elif self.position[1] <= 300 and self.position.move(round(-sin*F_VELOCITY), round(-cos*F_VELOCITY)).collidelist(walls) == -1:
                self.position.move_ip(round(-sin*F_VELOCITY), round(-cos*F_VELOCITY))
                self.dir = 0
            else:
            #if self.angle < 270 and self.angle > 90 and self.rot_center(self.my_tank_clean, self.position, self.angle+30)[1].collidelist(walls) == -1:
            #   self.angle += 30
            #   self.angle = self.angle % 360
            #    self.my_tank , self.position= self.rot_center(self.my_tank_clean, self.position, self.angle)
            #elif (self.angle > 270 or self.angle < 90) and self.rot_center(self.my_tank_clean, self.position, self.angle-30)[1].collidelist(walls) == -1:
            #    self.angle -= 30
            #    self.angle = self.angle % 360
            #    self.my_tank , self.position= self.rot_center(self.my_tank_clean, self.position, self.angle)
            #elif self.position[1] > 420 and self.position.move(round(sin*F_VELOCITY), round(cos*F_VELOCITY)).collidelist(walls) == -1:
            #    self.position.move_ip(round(sin*F_VELOCITY), round(cos*F_VELOCITY))
            #elif self.position[0] < 200 and self.position.move(round(-cos*S_VELOCITY), round(sin*S_VELOCITY)).collidelist(walls) == -1:
            #     self.position.move_ip(round(-cos*S_VELOCITY), round(sin*S_VELOCITY))
            #elif self.position[0] > 300 and self.position.move(round(cos*S_VELOCITY), round(-sin*S_VELOCITY)).collidelist(walls) == -1:
            #    self.position.move_ip(round(cos*S_VELOCITY), round(-sin*S_VELOCITY))
            #elif self.position[1] > 300 and self.position.move(round(-cos*S_VELOCITY), round(sin*S_VELOCITY)).collidelist(walls) == -1:
            #                self.position.move_ip(round(-cos*S_VELOCITY), round(sin*S_VELOCITY))
                ran_dir = randint(1, 4)
                if self.dir == 0:
                    if ran_dir == 1 and self.position.move(round(sin*F_VELOCITY), round(cos*F_VELOCITY)).collidelist(walls) == -1:
                        self.position.move_ip(round(sin*F_VELOCITY), round(cos*F_VELOCITY))
                    elif dir == 2 and self.position.move(round(-sin*F_VELOCITY), round(-cos*F_VELOCITY)).collidelist(walls) == -1:
                        self.position.move_ip(round(-sin*F_VELOCITY), round(-cos*F_VELOCITY))
                    elif dir == 3 and self.position.move(round(cos*S_VELOCITY), round(-sin*S_VELOCITY)).collidelist(walls) == -1:
                        self.position.move_ip(round(cos*S_VELOCITY), round(-sin*S_VELOCITY))
                    elif dir == 4 and self.position.move(round(-cos*S_VELOCITY), round(sin*S_VELOCITY)).collidelist(walls) == -1:
                        self.position.move_ip(round(-cos*S_VELOCITY), round(sin*S_VELOCITY))
                    self.dir = ran_dir
                elif self.dir == 1 and self.position.move(round(sin*F_VELOCITY), round(cos*F_VELOCITY)).collidelist(walls) == -1:
                    self.position.move_ip(round(sin*F_VELOCITY), round(cos*F_VELOCITY))
                elif self.dir == 2 and self.position.move(round(-sin*F_VELOCITY), round(-cos*F_VELOCITY)).collidelist(walls) == -1:
                    self.position.move_ip(round(-sin*F_VELOCITY), round(-cos*F_VELOCITY))
                elif self.dir == 3 and self.position.move(round(cos*S_VELOCITY), round(-sin*S_VELOCITY)).collidelist(walls) == -1:
                    self.position.move_ip(round(cos*S_VELOCITY), round(-sin*S_VELOCITY))
                elif self.dir == 4 and self.position.move(round(-cos*S_VELOCITY), round(sin*S_VELOCITY)).collidelist(walls) == -1:
                    self.position.move_ip(round(-cos*S_VELOCITY), round(sin*S_VELOCITY))
        screen.blit(self.my_tank, self.position)

#pygame.display.flip()


