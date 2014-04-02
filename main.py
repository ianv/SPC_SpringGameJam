#!/usr/bin/env python
import pygame, sys, os, random, math
from pygame.locals import *

pygame.init()
pygame.display.set_caption("IdontEven")
os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
clock = pygame.time.Clock()
dfltFont = pygame.font.SysFont('Arial', 20)
freq = 44100 # audio CD quality
bitsize = -16 # unsigned 16 bit
channels = 2 # 1= mono 2 = stereo
buffer = 2048 #number of samples (Experiment to get right sound)
pygame.mixer.init(freq, bitsize, channels, buffer)
pygame.mixer.music.set_volume(0.55)
HitSound = pygame.mixer.Sound(os.path.join('FX','HitSound.wav'))
HitSound.set_volume(.2)
global pause
pause = False
global I
I = False
global J
J = False
global CurrentLevel
CurrentLevel = 0

screen = pygame.display.set_mode((800, 600), 0, 32)

blocks = []
backgrounds = []
images = []

#mymusic.LoadMusic()
def fontTasks(text, pos, color = (20, 20, 20)):
	readyText = dfltFont.render(text, True, color)
	screen.blit(readyText, (pos[0], pos[1]))
	
		
class Menu():
	def __init__(self):
		self.InMenu = 1
		self.image = pygame.image.load(os.path.join('Images','Menu1.png')).convert_alpha()
		
	def render(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				if event.key == K_SPACE:
					self.InMenu = 0
		screen.blit(self.image,(0,0))
menu = Menu()
# Fade into a level. Start with black and go to white
class Transition():
	def __init__(self):
		self.maxTime = 80
		self.time = self.maxTime
		self.proceed = False
	def render(self):
		pygame.mixer.music.load(os.path.join('Music', 'level%d.ogg' %player.in_level)) #Load music file for current level
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				if self.time <= 10:
					self.proceed = True
		screen.fill(((0+self.time*3),(0+self.time*3),(0+self.time*3)))
		self.time -= 1
transition = Transition()

class Background():
	def __init__(self):
		if CurrentLevel > 3:
			self.image = pygame.image.load(os.path.join('Images', 'Background.png')).convert() #Imports image of forest from images folder
		else:
			self.image = pygame.image.load(os.path.join('Images', 'Background.png')).convert() #Imports image of forest from images folder
		self.x = 0
	def render(self):
		screen.blit(self.image, (self.x, -250))

		
BackG = Background()


#Clear out level and load a new one
def getRGB(level_num):
	BackG.x = 0
	if level_num > 3:
		BackG.image = pygame.image.load(os.path.join('Images', 'Background.png')).convert() #Imports image of forest from images folder
	else:
		BackG.image = pygame.image.load(os.path.join('Images', 'Background.png')).convert() #Imports image of forest from images folder
	del blocks[:], backgrounds[:], images[:]
	# Make sure player isn't moving and nullify his hit status; restore all stats to default
	player.dx = player.oldDX= player.hitBool = 0
	player.HP = player.maxHP
	player.x, player.y = 160, 50  #X and Y Starting location
	player.updateRect()
	transition.time = transition.maxTime # Reset trans time, which starts transition
	transition.proceed = False
	levelimg = pygame.image.load(os.path.join('Images', 'Level%d.png'%level_num)).convert_alpha()

	for x in range(levelimg.get_width()):
		for y in range(levelimg.get_height()):
			color = levelimg.get_at((x, y))
			if player.in_level <= 3:
				if color == (255, 255, 255, 255): # White = Red, Green, Blue, Alpha
					blocks.append(Dirt((x*20, y*16)))
				elif color == (255, 0, 0, 255): # Red
					blocks.append(Border((x*20, y*16))) #End of lvl
			if player.in_level >= 4 and player.in_level <= 6:
				if color == (255, 255, 255, 255): # White = Red, Green, Blue, Alpha
					blocks.append(Dirt2((x*20, y*16)))
				elif color == (255, 0, 0, 255): # Red
					blocks.append(Border((x*20, y*16))) #End of lvl


                    
class Block():
	def __init__(self, pos, imgType = None):
		self.x = pos[0]
		self.y = pos[1]
		self.offset = (0, 0)
		self.rect = pygame.Rect(self.x, self.y, 20, 16)
		self.color = (0, 0, 0)
		if imgType == 'Leaves':
			self.image = pygame.image.load(os.path.join('Images', 'Leaves%d.png')%random.randint(0, 1)).convert_alpha()
		elif imgType != 'Leaves' and imgType != None:
			self.image = pygame.image.load(os.path.join('Images', '%s.png')%imgType).convert_alpha()
		self.name = str(self.__class__)[9:] #Get the class's name
	def updateRect(self):
		self.rect.x, self.rect.y = self.x, self.y
	def render(self):
		screen.blit(self.image, (self.x, self.y))
		#pygame.draw.rect(screen, self.color, self.rect) #shows rects on screen filled with black
		
					
class Border(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)

class Player(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.rect = pygame.Rect(30, 30, 30, 30)
		self.image = pygame.Surface((30,30))
		self.image.fill((0,0,0))
		self.offset = (-2, 0)
		self.orig_y = self.y
		self.dx = 0
		self.oldDX = self.dx
		self.dy = 0
		self.direction = 1
		self.HP = 5
		self.maxHP = self.HP
		self.in_level = 1
		self.maxHeight = 60
		self.fallspeed = 0
		self.falling = False
		self.hitBool = 0
		self.A_Down = 0
		self.D_Down = 0
		self.jumpnum = 0
	# If hit, the player will be knocked in the opposite direction he was last moving
	def gotHit(self):
		self.HP -= 1
		self.hitBool = 1
		self.oldDX = self.dx
		if self.direction == 1:
			self.dx = -7.5
		else:
			self.dx = 7.5

	def move(self):
		global CurrentLevel
		# If you've been hit, forcefully slide back and then restore former speed
		if self.hitBool != 0:
			if self.dx > 0: self.dx -= .5
			if self.dx < 0: self.dx += .5
			if self.dx == 0:
				self.hitBool = 0
				self.dx = self.oldDX
		if self.dx > 0:
			self.direction = 1
		elif self.dx < 0:
			self.direction = -1
		# The player's x position never changes
		# Instead, we move blocks the opposite direction
		# If you collide with a block whilst moving on the x axis, undo the block movement
		BackG.x -= (self.dx * .15)
		for bg in backgrounds:
			bg.x -= self.dx
			bg.updateRect()
		for block in blocks:
			block.x -= self.dx
			block.updateRect()
			if self.rect.colliderect(block.rect):
				# Progress to next level upon hitting the border
				if block.name == "Border":
					self.in_level += 1
					getRGB(self.in_level)
				#Make sure enemies don't keep the x speed when player hits a wall
				for bg in backgrounds:
					bg.x += self.dx
					bg.updateRect()
				for each_block in blocks:
					each_block.x += self.dx
					each_block.updateRect()
				BackG.x += (self.dx * .15)
		self.gravity()
	def gravity(self):
		# Y axis movement, however, is normal.
		# Only the player moves Y-wise, so if he hits a block whilst falling,
		# only he gets pushed up; the block doesn't move.
		if self.falling == False:
			self.y += self.dy*2.2
			self.updateRect()
			self.fallspeed = 1.1
			if self.rect.y < self.orig_y-self.maxHeight-40:
				self.falling = True
				self.y += 5
			for block in blocks:
				#If you bump into a platform above you, fall
				if self.rect.colliderect(block.rect):
					self.rect.top = block.rect.bottom
					self.y = self.rect.y
					self.falling = True
					self.dy = 0
					break
				#If you walk off a platform, fall
				if self.rect.y == self.orig_y and self.rect.colliderect(block.rect) == False:
					self.falling = True
		#If falling... fall. If touching the ground, bring back ability to jump
		if self.falling == True:
			# Fall progressively faster
			self.y += self.fallspeed
			self.fallspeed += .3
			self.updateRect()
			#If you're on a platform, cease falling
			for block in blocks:
				if self.rect.colliderect(block.rect):
					self.rect.bottom = block.rect.top
					self.fallspeed = 0
					self.y = self.rect.y
					self.falling = False
					self.orig_y = self.rect.y
					break


class Foilage(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.rect = pygame.Rect(self.x,self.y, 175, 550)
		#self.rect.center = (16,8)
		self.image = pygame.image.load(os.path.join('Images', 'Tree2.png')).convert_alpha()
		
		
class Dirt(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.rect = pygame.Rect(self.x, self.y, 790, 100)
		#self.rect.center = (16,8)
		if player.in_level > 3:
			self.image = pygame.image.load(os.path.join('Images', 'ShallNotPass.tif')).convert_alpha()
		else:
			self.image = pygame.image.load(os.path.join('Images', 'ShallNotPass.tif')).convert_alpha()
			
			
class Dirt2(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.rect = pygame.Rect(self.x, self.y, 790, 100)
		#self.rect.center = (16,8)
		self.image = pygame.image.load(os.path.join('Images', 'DesertGroundTexture.tif')).convert_alpha()
					

player = Player((150, 50))

getRGB(1)
#play_music('level%d.ogg' %player.in_level)
# Event handling  
def inGame():
	screen.fill((0, 90, 70))
	global I
	global J
	global pause
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()

		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				pygame.quit()
				sys.exit()
			if event.key == K_SPACE:
				if player.falling == False:
					player.dy = -3.4
			if not pause:
				if event.key == K_d: #Move Right
					player.D_Down = 1
					player.dx = 3.8
				if event.key == K_a: #Move Left
					player.A_Down = 1
					player.dx = -3.8
			if event.key == K_n:
				getRGB(player.in_level)
			#if event.key == K_p:
			#	getRGB(3)
			if event.key == K_RETURN:
				pause = False
								
		if event.type == KEYUP:
			if event.key == K_SPACE:
				if player.dy < 0:
					player.dy = 0
					player.falling = True
					
			if event.key == K_d:
				player.D_Down = 0
			if event.key == K_a:
				player.A_Down = 0
			if player.A_Down == 0 and player.D_Down == 0:
				player.dx = 0
				player.oldDX = 0
			if event.key == K_RETURN:
				pause = False

	
	# move the player first so everything moves with it
	# then render the player AFTER the BGs so it's on top of them
	if not pause:
		player.move()

	#renders everything on screen
	screen.blit(BackG.image, (BackG.x,-250))
	
	for bg in backgrounds:
		bg.render()
		
	player.render()
	
	for block in blocks:
		if block.name != "Border":
			block.render()
		
	if player.HP < 0 or player.y > screen.get_height() + 10:
		getRGB(player.in_level)
	
			
while True:
	if menu.InMenu > 0:
		menu.render()
	elif transition.time > 1:
		transition.render()
		pygame.mixer.music.play() #This works and will play music based on level
		
	else:
		inGame()
	clock.tick(60)
	
	pygame.display.flip()