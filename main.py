from __future__ import print_function, division
import pygame
import random
import math
from random import randint
from field_map import *
from constant import *
GRAD = math.pi / 180
NUM_OBSERVATION = 4
WALL_PUB = 100
CENTER_PARAM = 0.1
ON_REWARD = 100
GET_REWARD = 10
class Text(pygame.sprite.Sprite):
    """ a helper class to write text on the screen """
    number = 0 
    book = {}
    def __init__(self, pos, msg):
        self.number = Text.number # get a unique number
        Text.number += 1 # prepare number for next Textsprite
        Text.book[self.number] = self # store myself into the book
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.pos = [0.0,0.0]
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
        self.msg = msg
        self.changemsg(msg)

 
    def changemsg(self,msg):
        self.msg = msg
        self.image = write(self.msg)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.pos[0]
        self.rect.centery = self.pos[1]


#####    Bullet Class     ####
################################
##--------------------------------------------------------------------------------
class Bullet(pygame.sprite.Sprite):
    """ a big projectile fired by the tank's main cannon"""
    side = 2 # small side of bullet rectangle
    vel = BULLET_VEL # velocity
    mass = 50
    maxlifetime = 10.0 # seconds
    spawn_position = 60
    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.boss = boss
        self.dx = 0
        self.dy = 0
        self.angle = 0
        self.lifetime = 0.0
        self.color = self.boss.color
        self.calculate_heading()
        self.dx += self.boss.dx
        self.dy += self.boss.dy # add boss movement
        self.pos = self.boss.pos[:] # copy of boss position 
        #self.pos = self.boss.pos   # uncomment this linefor fun effect
        self.calculate_origin()
        self.update(np.zeros((12, ))) # to avoid ghost sprite in upper left corner, 
                      # force position calculation.
 
    def calculate_heading(self):
        """ drawing the bullet and rotating it according to it's launcher"""
        self.radius = Bullet.side # for collision detection
        self.angle += self.boss.turretAngle
        self.mass = Bullet.mass
        self.vel = Bullet.vel
        image = pygame.Surface((Bullet.side, Bullet.side)) # rect 2 x 1
        image.fill((255,255,255)) # fill grey
        pygame.draw.rect(image, self.color, (0,0,int(Bullet.side), Bullet.side)) # rectangle 1.5 length
        pygame.draw.circle(image, self.color, (int(self.side) ,self.side//2), self.side//2) #  circle
        image.set_colorkey((128,128,128)) # grey transparent
        #self.image0 = image.convert_alpha()
        self.image = pygame.transform.rotate(image, self.angle)
        self.rect = self.image.get_rect()
        self.dx = math.cos(degrees_to_radians(self.boss.turretAngle)) * self.vel
        self.dy = math.sin(degrees_to_radians(-self.boss.turretAngle)) * self.vel
 
    def calculate_origin(self):
        self.pos[0] +=  math.cos(degrees_to_radians(self.boss.turretAngle)) * (Tank.side-Bullet.spawn_position)
        self.pos[1] +=  math.sin(degrees_to_radians(-self.boss.turretAngle)) * (Tank.side-Bullet.spawn_position)
 
    def update(self, action, seconds=0.0):
        # ---- kill if too old ---
        self.lifetime += seconds
        if self.lifetime > Bullet.maxlifetime:
            self.kill()
        # ------ calculate movement --------
        self.pos[0] += self.dx * seconds
        self.pos[1] += self.dy * seconds
        # ----- kill if out of screen
        if self.pos[0] < 0:
            self.kill()
        elif self.pos[0] > MAP_WIDTH:
            self.kill()
        if self.pos[1] < 0:
            self.kill()
        elif self.pos[1] > MAP_HEIGHT:
            self.kill()
        #------- move and collision detect-------
        try:
            self.rect.centerx = round(self.pos[0],0)
            self.rect.centery = round(self.pos[1],0)
        finally:
            if self.rect.collidelist(WALL_LIST) != -1 or self.rect.collidelist(self._tank_rect_ls()) != -1:
                self._hurt()
                self.kill()
    
    def reset(self):
        pass


    def _tank_rect_ls(self):
        temp = []
        for i in range(len(Tank.book)):
            temp.append(Tank.book[i].get_rect())
        return temp

    def _hurt(self):
        index = self.rect.collidelist(self._tank_rect_ls())
        if index != -1:
            self.boss.ontarget += 1
            self.boss.reward += ON_REWARD
            Tank.book[index].hp -= 20 * self.boss.attack_buff
            Tank.book[index].reward -= GET_REWARD




##### In Sight Detection  ####
##############################
##--------------------------------------------------------------------------------
####################################################################################################
####################################################################################################
####################################################################################################
class LineOfSight(pygame.sprite.Sprite):
    """ a big projectile fired by the tank's main cannon"""
    side = 2 # small side of bullet rectangle
    maxlifetime = 10.0 # seconds
    def __init__(self, boss, target):
        pygame.sprite.Sprite.__init__(self)
        self.boss = boss
        self.angle = 0
        self.target = target
        self.lifetime = 0.0
        self.color = self.boss.color
        self.calculate_heading()
        self.dx = (self.target.pos[0]-self.boss.pos[0])/20
        self.dy = (self.target.pos[1]-self.boss.pos[1])/20
        self.pos = self.boss.pos[:] # copy of boss position
        #self.pos = self.boss.pos   # uncomment this linefor fun effect
        self.result = self.is_in_sight()
        # to avoid ghost sprite in upper left corner,
    # force position calculation.
    
    def calculate_heading(self):
        """ drawing the line of sight """
        self.radius = LineOfSight.side # for collision detection
        image = pygame.Surface((LineOfSight.side, LineOfSight.side)) # rect 2 x 1
        image.fill((255,255,255)) # fill grey
        pygame.draw.rect(image, self.color, (0,0,int(LineOfSight.side), LineOfSight.side)) # rectangle 1.5 length
        pygame.draw.circle(image, self.color, (int(self.side) ,self.side//2), self.side//2) #  circle
        image.set_colorkey((128,128,128)) # grey transparent
        #self.image0 = image.convert_alpha()
        self.image = pygame.transform.rotate(image, self.angle)
        self.rect = self.image.get_rect()
    
    
    def is_in_sight(self):
        #------- move and collision detect-------
        for i in range(19):
            try:
                self.rect.centerx = round(self.pos[0],0)
                self.rect.centery = round(self.pos[1],0)
            finally:
                if self.rect.collidelist(WALL_LIST) != -1:
                    #                 self.kill()
                    return False
                self.pos[0] += self.dx
                self.pos[1] += self.dy
                    #   self.kill()
        return True
####################################################################################################
####################################################################################################
####################################################################################################







##### Tank Class  ####
##############################
##--------------------------------------------------------------------------------
class Tank(pygame.sprite.Sprite):
    side = 100 # side of the quadratic tank sprite
    recoiltime = 1 # how many seconds  the cannon is busy after firing one time
    turretTurnSpeed = 36 # turret
    tankTurnSpeed = 36 # tank
    f_movespeed = F_VELOCITY
    s_movespeed = S_VELOCITY
    maxhp =2000
    # maxrotate = 360 # maximum amount of degree the turret is allowed to rotate
    book = {} # a list of all tanks
    player = True # side
    number = 0 # each tank gets his own number
    maxturrentangle = 110 #turrent limit
    reward = 0
    color = ((255,255,255))
    msg = ["wxad for up down left right, qezc for upleft upright downleft downright, j and k for turning left and right."]
 
    def __init__(self, startpos = (150,150), angle=0, playerSide=True):
        self.init_angle = angle
        self.number = Tank.number # now i have a unique tank number
        self.player = playerSide
        Tank.number += 1 # prepare number for next tank
        Tank.book[self.number] = self # store myself into the tank book
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.hp = Tank.maxhp
        self.startpos = [startpos[0], startpos[1]]
        self.pos = [startpos[0], startpos[1]] # x,yself.pos = [startpos[0], startpos[1]]
        self.dx = 0
        self.dy = 0
        self.ammo = 300 # main gun
        self.msg =  "player%i: ammo: %i hp: %i" % (self.number+1, self.ammo, self.hp)
        Text((MAP_WIDTH/2, 30+20*self.number), self.msg) # create status line text sprite
        self.color = Tank.color[self.number]
        self.turretAngle = angle #turret facing
        self.tankAngle = angle # tank facing
        #----------key control------------------#
        #self.firekey = Tank.firreturekey[self.number] # main gun     
        # self.turretLeftkey = Tank.turretLeftkey[self.number] # turret
        # self.turretRightkey = Tank.turretRightkey[self.number] # turret
        # self.forwardkey = Tank.forwardkey[self.number] # move tank
        # self.backwardkey = Tank.backwardkey[self.number] # reverse tank
        # self.tankLeftkey = Tank.tankLeftkey[self.number] # tank go with left
        # self.tankRightkey = Tank.tankRightkey[self.number] # tank go with right
        # self.tankTurnleftkey = Tank.tankTurnleftkey[self.number] # rotate
        # self.tankTurnrightkey = Tank.tankTurnrightkey[self.number] #  rotate
        # self.rightForwardkey = Tank.rightForwardkey[self.number] # right forward
        # self.rightBackwardkey = Tank.rightBackwardkey[self.number] # right backward
        # self.leftForwardkey = Tank.leftForwardkey[self.number] # left forward
        # self.leftBackwardkey = Tank.leftBackwardkey[self.number] # left backward
        self.turretLeftkey = 11 # turret
        self.turretRightkey = 10 # turret
        self.forwardkey = 2 # move tank
        self.backwardkey = 6 # reverse tank
        self.tankLeftkey = 0 # tank go with left
        self.tankRightkey = 4 # tank go with right
        self.tankTurnleftkey = 9 # rotate
        self.tankTurnrightkey = 8 #  rotate
        self.rightForwardkey = 3 # right forward
        self.rightBackwardkey = 5 # right backward
        self.leftForwardkey = 1 # left forward
        self.leftBackwardkey = 7 # left backward
        self.dir = 0
        self.target = self
        self.ontarget = 0
        self.dead = False
        self.attack_buff = 1
        self.count = 0

        # painting facing north, have to rotate 90° later
        image = pygame.Surface((Tank.side,Tank.side)) # created on the fly
        if self.player:
            self.color = (0,0,255)
        else:
            self.color = (255,0,0)
        image.fill(self.color) # fill RED for enemy; BLUE for player
        if self.side > 10:
             pygame.draw.rect(image, (128,128,128), (5,5,self.side-10, self.side-10)) #tank body, margin 5
             pygame.draw.rect(image, (90,90,90), (0,0,self.side//6, self.side)) # track left
             pygame.draw.rect(image, (90,90,90), (self.side-self.side//6, 0, self.side,self.side)) # right track
             pygame.draw.rect(image, self.color, (self.side//6+5 , 10, 10, 5)) # red bow rect left
             #pygame.draw.rect(image, (255,0,0), (self.side/2 - 5, 10, 10, 5)) # red bow rect middle
        pygame.draw.circle(image, (0,0,0), (self.side//2,self.side//2), self.side//3 , 2) # red circle for turret
        image = pygame.transform.scale(pygame.transform.rotate(image,-90),(TANK_WID,TANK_HEI)) # rotate so to look east
        self.image0 = image.convert_alpha()
        self.image = image.convert_alpha()
        self.rect = self.image0.get_rect()
        #---------- turret ------------------
        self.firestatus = 0.0 # time left until cannon can fire again
        self.turndirection = 0    # for turret
        self.tankturndirection = 0
        self.f_movespeed = Tank.f_movespeed
        self.s_movespeed = Tank.s_movespeed
        self.turretTurnSpeed = Tank.turretTurnSpeed
        self.tankTurnSpeed = Tank.tankTurnSpeed
        Turret(self) # create a Turret for this tank
        #---------bonus-------------#
        self.bonus_position = Bonus().rect
        self.break_loop = False
        self.buff = False
        self.line1 = None
        self.observation = np.zeros((NUM_OBSERVATION, ))

    def get_rect(self):
        return self.rect

    def update_buff(self, flag):

        timer_flag = True
        while self.bonus_position.contains(self.rect) == 1 and not self.break_loop:
            if timer_flag:
                start = time.time()
                timer_flag = False
            if time.time() - start > 5:
                flag = True
                self.break_loop = True
                if self.player:
                    Tank.book[0].attack_buff = 1.5
                else:
                    Tank.book[1].attack_buff = 1.5
                    Tank.book[2].attack_buff = 1.5
        return flag


    def rot_center(self, image, old_image, rect, angle):
        """rotate an image while keeping updating its center and size"""
        oldcenter = rect.center
        oldrect = image.get_rect()
        image  = pygame.transform.rotate(old_image, angle) 
        rect = image.get_rect()
        rect.center = oldcenter 
        return image, rect
    
        
    def biggerthan(self,angle1,angle2):
        angle1 = angle1 % 360
        angle2 = angle2 % 360
        if angle2 < 180:
            return angle1 > angle2
        else:
            return self.biggerthan(angle2-180,angle1)

    def update(self, action, seconds):
        #-------- reloading, firestatus----------
        if self.firestatus > 0:
            self.firestatus -= seconds # cannon will soon be ready again
            if self.firestatus <0:
                self.firestatus = 0 #avoid negative numbers
        # ------------ keyboard --------------
       # pressedkeys = pygame.key.get_pressed()
        # -------- turret rotation ----------
        self.turndirection = 0    #  left / right turret rotation
        dist = []
        if self.player and not self.dead:
            for i in range(2):
                robot = Tank.book[i+1]
                if not robot.dead:
                    dist.append(((self.pos[0] - robot.pos[0])**2 + (self.pos[1] - robot.pos[1])**2) ** 0.5)
                else:
                    dist.append(999999999) # Set the distance to infinite if dead
            if dist[0] <= dist[1]:
                self.target = Tank.book[1]
            else:
                self.target = Tank.book[2]
            angle = radians_to_degrees(math.atan2(-self.target.pos[1]+self.pos[1],self.target.pos[0]-self.pos[0]))
            if (angle%360 - self.turretAngle%360)> 6 and self.biggerthan(angle,self.turretAngle) and self.biggerthan(self.turretAngle+180,angle) and not self.dead:
                self.turndirection += 1
            else:
                if not self.dead:
                    self.turndirection -= 1
        elif not self.player and not self.dead:
            self.target = Tank.book[0]
            angle = radians_to_degrees(math.atan2(-self.target.pos[1]+self.pos[1],self.target.pos[0]-self.pos[0]))
            if (angle%360 - self.turretAngle%360)> 6 and self.biggerthan(angle,self.turretAngle) and self.biggerthan(self.turretAngle+180,angle):
                self.turndirection += 1
            else:
                self.turndirection -= 1


       #if pressedkeys[self.turretLeftkey]:
        if action == self.turretLeftkey:
            self.turndirection += 1
        if action == self.turretRightkey:
            self.turndirection -= 1
 
        #---------- tank rotation ---------
        self.tankturndirection = 0 # reset left/right rotation
        if self.player and not self.dead:
            if action == self.tankTurnleftkey:
                self.tankturndirection += 1
            if action == self.tankTurnrightkey:
                self.tankturndirection -= 1
        elif not self.player and not self.dead:
            if self.tankAngle%360 > 275 or self.tankAngle%360 < 85:
                self.tankturndirection -= 1
            elif self.tankAngle%360 >95 or self.tankAngle%360 < 265:
                self.tankturndirection += 1
        # ---------------- rotate tank and turret and collisiton detect ---------------
        self.tankAngle += self.tankturndirection * self.tankTurnSpeed * seconds # time-based turning of tank
        try:
            self.image, self.rect = self.rot_center(self.image, self.image0, self.rect, self.tankAngle)
            self.turretAngle += self.tankturndirection * self.tankTurnSpeed * seconds  + self.turndirection * self.turretTurnSpeed * seconds # time-based turning
        finally:
            if self.rect.collidelist(WALL_LIST) != -1  or self.rect.collidelist(self._othertank_rect()) != -1:
                self.tankAngle -= self.tankturndirection * self.tankTurnSpeed * seconds # time-based turning of tank
                self.image, self.rect = self.rot_center(self.image, self.image0, self.rect, self.tankAngle)
                self.turretAngle -= self.tankturndirection * self.tankTurnSpeed * seconds  + self.turndirection * self.turretTurnSpeed * seconds # time-based turning
                #self.reward -= WALL_PUB
        if self.turretAngle - self.tankAngle > Tank.maxturrentangle:
            self.turretAngle = Tank.maxturrentangle + self.tankAngle
        elif self.turretAngle - self.tankAngle < -Tank.maxturrentangle:
            self.turretAngle = -Tank.maxturrentangle + self.tankAngle
####################################################################################################
####################################################################################################
####################################################################################################
        # ---------- fire cannon -----------
        if (self.firestatus ==0) and (self.ammo > 0) and not self.dead:
            self.line1 = LineOfSight(self,self.target)
            if self.line1.result:
                self.firestatus = Tank.recoiltime # seconds until tank can fire again
                Bullet(self)    
                self.ammo -= 1
                self.msg =  "player%i: ammo: %i HP: %s Ontarget: %i" % (self.number+1, self.ammo, self.hp, self.ontarget)
                Text.book[self.number].changemsg(self.msg)
        
####################################################################################################
####################################################################################################
####################################################################################################
        # ---------- movement ------------
        self.dx = 0
        self.dy = 0
        self.forward = 0 # movement calculator
        self.right  = 0 # drifting calculator
        self.leftforward = 0
        self.rightforward = 0
        if self.player and not self.dead:
            if action == self.forwardkey:
                self.forward += 1
            if action == self.backwardkey:
                self.forward -= 1
            if action == self.tankRightkey:
                self.right += 1
            if action == self.tankLeftkey:
                self.right -= 1
            if action == self.leftForwardkey:
                self.leftforward += 1
            if action == self.leftBackwardkey:
                self.leftforward -= 1
            if action == self.rightForwardkey:
                self.rightforward += 1
            if action == self.rightBackwardkey:
                self.rightforward -= 1
        elif not self.player and not self.dead:
            if self.pos[1] <= 250:
                self.forward += 1
                self.dir = 0
            elif self.pos[0] <= 220:
                self.right -= 1
                self.dir = 0
            elif self.pos[0] >= 300:
                self.right += 1
                self.dir = 0
            elif self.pos[1] >= 420:
                self.forward -= 1
                self.dir = 0
            elif self.dir == 0:
                ran_dir = randint(1,4)
                if ran_dir == 1:
                    self.forward = 1
                    self.dir = ran_dir
                elif ran_dir == 2:
                    self.forward = -1
                    self.dir = ran_dir
                elif ran_dir == 3:
                    self.right = 1
                    self.dir = ran_dir
                elif ran_dir == 4:
                    self.right = -1
                    self.dir = ran_dir
            elif self.dir == 1:
                self.forward = 1
            elif self.dir == 2:
                self.forward = -1
            elif self.dir == 3:
                self.right = 1
            elif self.dir == 4:
                self.right = -1
        # if both are pressed togehter, self.forward becomes 0
        if self.forward == 1:
            self.dx =  math.cos(degrees_to_radians(self.tankAngle)) * self.f_movespeed
            self.dy =  -math.sin(degrees_to_radians(self.tankAngle)) * self.f_movespeed
        elif self.forward == -1:
            self.dx =  -math.cos(degrees_to_radians(self.tankAngle)) * self.f_movespeed
            self.dy =  math.sin(degrees_to_radians(self.tankAngle)) * self.f_movespeed
        elif self.right == 1:
            self.dx =  math.sin(degrees_to_radians(self.tankAngle)) * self.s_movespeed
            self.dy =  math.cos(degrees_to_radians(self.tankAngle)) * self.s_movespeed
        elif self.right == -1:
            self.dx =  -math.sin(degrees_to_radians(self.tankAngle)) * self.s_movespeed
            self.dy =  -math.cos(degrees_to_radians(self.tankAngle)) * self.s_movespeed
        elif self.leftforward == 1:
            self.dx = (math.cos(degrees_to_radians(self.tankAngle)) * self.f_movespeed -math.sin(degrees_to_radians(self.tankAngle)) * self.s_movespeed)/4
            self.dy = (-math.sin(degrees_to_radians(self.tankAngle)) * self.f_movespeed  -math.cos(degrees_to_radians(self.tankAngle)) * self.s_movespeed)/4
        elif self.leftforward == -1:
            self.dx = -(math.cos(degrees_to_radians(self.tankAngle)) * self.f_movespeed + math.sin(degrees_to_radians(self.tankAngle)) * self.s_movespeed)/4
            self.dy = -(-math.sin(degrees_to_radians(self.tankAngle)) * self.f_movespeed  + math.cos(degrees_to_radians(self.tankAngle)) * self.s_movespeed)/4
        elif self.rightforward == 1:
            self.dx = (math.cos(degrees_to_radians(self.tankAngle)) * self.f_movespeed + math.sin(degrees_to_radians(self.tankAngle)) * self.s_movespeed)/4
            self.dy = (-math.sin(degrees_to_radians(self.tankAngle)) * self.f_movespeed  + math.cos(degrees_to_radians(self.tankAngle)) * self.s_movespeed)/4
        elif self.rightforward == -1:
            self.dx = -(math.cos(degrees_to_radians(self.tankAngle)) * self.f_movespeed -math.sin(degrees_to_radians(self.tankAngle)) * self.s_movespeed)/4
            self.dy = -(-math.sin(degrees_to_radians(self.tankAngle)) * self.f_movespeed  -math.cos(degrees_to_radians(self.tankAngle)) * self.s_movespeed)/4


        self.pos[0] += self.dx * seconds
        self.pos[1] += self.dy * seconds
        # ------------- check collision ---------------------
        try:
            self.rect.centerx = round(self.pos[0], 0) #x
            self.rect.centery = round(self.pos[1], 0) #y
        finally: 
            if self.rect.collidelist(WALL_LIST) != -1 or self.rect.collidelist(self._othertank_rect()) != -1:
                self.pos[0] -= self.dx * seconds
                self.pos[1] -= self.dy * seconds
                self.rect.centerx = round(self.pos[0], 0) #x
                self.rect.centery = round(self.pos[1], 0) #y
                self.dir = 0
                self.reward -= WALL_PUB
                self.count += 1
        self.reward += (np.abs(self.pos[0] - 500) + np.abs(self.pos[1] - 800))*CENTER_PARAM
        #--------------update bonus--------------------#
        self.buff = self.update_buff(self.buff)
        self._dead()
        self.observation = np.array([self.pos[0], self.pos[1],
                                self.tankAngle%360, self.turretAngle%360 ])

    def reset(self):
        self.dead = False
        self.hp = 2000
        if self.player:
            self.turretAngle = 90 #turret facing
            self.tankAngle = 90 # tank facing
        else:
            self.turretAngle = -90 #turret facing
            self.tankAngle = -90 # tank facing
        self.pos = [self.startpos[0], self.startpos[1]] # x,y
        self.dx = 0
        self.dy = 0
        self.ammo = 300 # main gun
        #self.dir = 0
        #self.target = self
        self.ontarget = 0
        self.dead = False
        self.attack_buff = 1
        #self.line1 = None
        self.count = 0

#,self.line1 * 1
    def get_return(self):
        return self.reward, self.observation, self.dead

#----------------return other tank's rect--------------#
    def _othertank_rect(self):
        temp = []
        for i in range(len(Tank.book)):
            if i != self.number:
                temp.append(Tank.book[i].get_rect())
        return temp
    
    def _dead(self):
        if (self.hp < 0 or self.count > 500) and self.player:
            self.dead = True


#####     Turret Class     ####
###############################
##--------------------------------------------------------------------------------
class Turret(pygame.sprite.Sprite):
    """turret on top of tank"""
    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.boss = boss
        self.side = self.boss.side    
        self.images = {} # how much recoil after shooting, reverse order of apperance
        self.images[0] = self.draw_cannon(0)  # idle position
        self.images[1] = self.draw_cannon(1)
        self.images[2] = self.draw_cannon(2)
        self.images[3] = self.draw_cannon(3)
        self.images[4] = self.draw_cannon(4)
        self.images[5] = self.draw_cannon(5)
        self.images[6] = self.draw_cannon(6)
        self.images[7] = self.draw_cannon(7)
        self.images[8] = self.draw_cannon(8)  # position of max recoil
        self.images[9] = self.draw_cannon(4)
        self.images[10] = self.draw_cannon(0) # idle position
 
    def update(self, action, seconds):        
        # painting the correct image of cannon
        if self.boss.firestatus > 0:
            self.image = self.images[int(self.boss.firestatus // (Tank.recoiltime / 10.0))]
        else:
            self.image = self.images[0]
        # --------- rotating -------------
        # angle etc from Tank (boss)
        oldrect = self.image.get_rect() # store current surface rect
        self.image  = pygame.transform.rotate(self.image, self.boss.turretAngle) 
        self.rect = self.image.get_rect()
        # ---------- move with boss ---------
        self.rect = self.image.get_rect()
        self.rect.center = self.boss.rect.center
 
    def draw_cannon(self, offset):
         # painting facing right, offset is the recoil
         image = pygame.Surface((self.boss.side * 2,self.boss.side * 2)) # created on the fly
         image.fill((128,128,128)) # fill grey
         pygame.draw.circle(image, (255,0,0), (self.side,self.side), 22, 0) # red circle
         pygame.draw.circle(image, (0,255,0), (self.side,self.side), 18, 0) # green circle
         pygame.draw.rect(image, (255,0,0), (self.side-10, self.side + 10, 15,2)) # turret mg rectangle
         pygame.draw.rect(image, (0,255,0), (self.side-20 - offset,self.side - 5, self.side - offset,10)) # green cannon
         pygame.draw.rect(image, (255,0,0), (self.side-20 - offset,self.side - 5, self.side - offset,10),1) # red rect 
         image = pygame.transform.scale(image, (80, 120))
         image.set_colorkey((128,128,128))
         return image

    def reset(self):
        pass
# ---------------- End of classes --------------------
                            
                            
                        
                            
                            
#------------ defs ------------------
def radians_to_degrees(radians):
    return (radians / math.pi) * 180.0
 
def degrees_to_radians(degrees):
    return degrees * (math.pi / 180.0)
 
def write(msg="pygame is cool"):
    """helper function for the Text sprite"""
    myfont = pygame.font.SysFont("None", 28)
    mytext = myfont.render(msg, True, (255,255,0))
    mytext = mytext.convert_alpha()
    return mytext        


