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
global NPCcontact 
NPCcontact = False
global CurrentLevel
CurrentLevel = 0

screen = pygame.display.set_mode((800, 600), 0, 32)

blocks = []
backgrounds = []
spells = []
enemySpells = []
enemies = []
npcs = []
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
	del blocks[:], enemies[:],npcs[:], backgrounds[:], spells[:], enemySpells[:], images[:]
	# Make sure player isn't moving and nullify his hit status; restore all stats to default
	player.dx = player.oldDX= player.hitBool = 0
	player.HP = player.maxHP
	#image1 = pygame.image.load(os.path.join('Images','bone.png'))
	#image2 = pygame.image.load(os.path.join('Images','bone.png'))
	#image3 = pygame.image.load(os.path.join('Images','bone.png'))
	#image4 = pygame.image.load(os.path.join('Images','bone.png'))
	#image5 = pygame.image.load(os.path.join('Images','bone.png'))
	#images.append(image1)
	#images.append(image2)
	#images.append(image3)
	#images.append(image4)
	#images.append(image5)
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
				elif color == (0, 255, 0, 255):
					backgrounds.append(Block((x*20, y*16), 'Leaves'))
				#elif color == (136, 0, 21, 255): #Maroon 
				#	blocks.append(Beehive((x*20, y*16))) #Adds beehive


                    
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
				for enemy in enemies:
					enemy.move_x = False
				for npc in npcs:
					npc.move_x = False
				for spell in spells:
					if spell.name != "Leaf":
						spell.move_x = False
				for enemySpell in enemySpells:
					enemySpell.move_x = False
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


#NPC class
class NPC(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.dx = 0
		self.move_x = True
	
#Bear NPC you learn first skill from
class Stelio(Block):
	def __init__(self,pos):
		Block.__init__(self, pos)
		self.dx = 0
		self.move_x = True
		self.name = 'Stelio'
		self.rect = pygame.Rect(self.x, self.y, 85, 101)
		self.image = pygame.image.load(os.path.join('Images', 'Stelio3.png')).convert_alpha()
	def move(self):
		if self.move_x == True:
			self.x -= player.dx
		self.updateRect()
		self.move_x = True
#Cub NPC you rescue from first hunter
class Cub(Block):
	def __init__(self,pos):
		Block.__init__(self, pos)
		self.dx = 0
		self.move_x = True
		self.name = 'Cub'
		self.rect = pygame.Rect(self.x, self.y, 70, 113)
		self.image = pygame.image.load(os.path.join('Images', 'cub2.png')).convert_alpha()
		self.image2 = pygame.image.load(os.path.join('Images', 'Cage.png')).convert_alpha()
	def move(self):
		if self.move_x == True:
			self.x -= player.dx
		self.updateRect()
		self.move_x = True

class BigBear(Block):
	def __init__(self,pos):
		Block.__init__(self, pos)
		self.rect = pygame.Rect(self.x, self.y, 130, 246)
		self.image = pygame.image.load(os.path.join('Images', 'bigbear.png')).convert_alpha()

#Enemy Class
class crow(Block):
	def __init__(self,pos):
		Block.__init__(self, pos)
		self.stunTime = 0
		self.life = 4
		self.dx = random.choice([.5, .7, .9])
		self.dy = random.choice([.5, .7, .9]) 
		self.screen_x = screen.get_width()
		self.rect = pygame.Rect(self.x, self.y, 20,16 )
		self.image = pygame.image.load(os.path.join('Images','crow2.png')).convert_alpha()
		self.originalimage = pygame.Surface.copy(self.image)
		self.offset = (-4, -8)
		self.move_x = True
	def move(self):
		if self.stunTime <= 0:
			if self.x < self.screen_x + 10 and self.x > -10:
				if player.x < self.x:
					self.x -= self.dx
				if player.x > self.x:
					self.x += self.dx	
				#Crow goes down as far as the player's y - 3
				if player.y*1.08 > self.y:    #Multiplying by 1.08 shifts the crows flight path down, higher multiplier makes the crow go lower
					self.y += self.dy
				if player.y*1.08 < self.y:
					self.y -= self.dy
		#Also subtract the player's x movement so it moves with the screen, but only when the player isn't
		#colliding with a wall on during x movement
		if self.move_x == True:
			self.x -= player.dx
		self.updateRect()
		self.move_x = True
	
		
class skunk(Player):
	def __init__(self, pos):
		Player.__init__(self, pos)
		self.dx = 0 #random.choice([.5, .7, .9])
		self.stunTime = 0
		self.maxHeight = 1
		self.falling = True
		self.rect = pygame.Rect(self.x, self.y, 20, 35)
		self.image = pygame.image.load(os.path.join('Images','Skunk3.png')).convert_alpha()
		self.life = 3
		self.move_x = True
		self.attackTime = 0
	# We're just using the player's gravity function and a modification of his move function
	# Instead of having blocks move away like when the player bumps them, the Runner gets pushed away
	def move(self):
		if self.stunTime <= 0:
			if player.x < self.x and self.x < 455:
				self.dx = -random.choice([.5, .7, .9])
				self.attackTime += 1
			elif player.x >= self.x and self.x > 0:
				self.dx = random.choice([.5, .7, .9])
				self.attackTime += 1
			# Attack every 85 frames
			if self.attackTime == 55:
				self.attack()
			self.x += self.dx
		if self.move_x == True:
			self.x -= player.dx
		self.updateRect()
		# Only check for collision with walls if actually moving
		if self.dx != 0:
			for block in blocks:
				if self.rect.colliderect(block.rect):
					self.dy = -2.5
					if self.dx < 0:
						self.rect.left = block.rect.right
					elif self.dx > 0:
						self.rect.right = block.rect.left
					self.x = self.rect.x
		self.move_x = True
		self.gravity()
	def attack(self):
		self.attackTime = 0
		
		
			
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
			
class Beehive(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.rect = pygame.Rect(self.x, self.y, 46, 40)
		#self.rect.center = (16,8)
		self.image = pygame.image.load(os.path.join('Images', 'Beehive2.png')).convert_alpha()
		

class TopDirt(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.rect = pygame.Rect(self.x, self.y, 24, 16)
		self.image = pygame.image.load(os.path.join('Images', 'tiletop.tif')).convert_alpha()
		
class Boss1(Player):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.image = pygame.image.load(os.path.join('Images','HunterBoss1.png')).convert_alpha()
		self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
		self.life = 80
		self.move_x = True
		self.orig_y = 0
		self.dy = 10.2
		self.dx = 0
		self.attackTime = 0
	def move(self):
		self.attackTime += 1
		if self.attackTime == 65:
			self.attack()
		if self.move_x == True:
			self.x -= player.dx	
		self.updateRect()
		self.move_x = True
	def render(self):
		screen.blit(self.image, (self.x, self.y))
	# 3 types of attacks, straight shot, targeted shot, and shotgun spray
	def attack(self):
		self.attackTime = 0
		enemySpells.append(Bullet((self.x, self.y+(80))))
		if self.x < player.x:
			
			bulletDY = 4
		else:
			bulletDY = -4
		
			

class Bullet(Block):
	def __init__(self, pos, dx = 0, dy = 0):
		Block.__init__(self, pos)
		self.y = self.y-65
		self.move_x = True
		if self.x < player.x:
			self.dx = 3.5
		else:
			self.dx = -3.5
		self.dy = math.sin(math.radians(player.y-self.y))*2
		self.image = pygame.image.load(os.path.join('Images','rock.png')).convert_alpha()
		self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
	def move(self):
		self.x += self.dx
		self.y += self.dy
		if self.move_x == True:
			self.x -= player.dx
		self.move_x = True
		self.updateRect()
				
class Rock(Block):
	def __init__(self):
		if player.direction == 1:
			self.x = player.x + 16
			self.dx = 4.9
		else:
			self.x = player.x
			self.dx = -4.9
		Block.__init__(self, (self.x, player.y+40))
		self.move_x = True
		self.time = 65
		self.image = pygame.image.load(os.path.join('Images','rock.png')).convert_alpha()
		self.origImage = self.image
		self.height = self.image.get_height()
		self.width = self.image.get_width()
	def move(self):
		self.x += self.dx
		if self.move_x == True:
			self.x -= player.dx
		self.y += .3
		#self.y -= .5
		self.updateRect()
		self.time -= 1
		self.move_x = True
		



player = Player((150, 50))

getRGB(1)
#play_music('level%d.ogg' %player.in_level)
# Event handling  
def inGame():
	screen.fill((0, 90, 70))
	global I
	global J
	global pause
	global NPCcontact 
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
			if event.key == K_RCTRL:
				if I == True and NPCcontact == True and J == False:
					spells.append(Rock())
					#Rockthrow.play()
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
			if event.key == K_i:
				if NPCcontact == True:
					I = True
					pause = False
			if event.key == K_j:
				if NPCcontact == True:
					J = True
					player.maxHeight=100
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
		if block.name == 'BigBear':
			#Error checking
			try:
				for spell in spells: 
					if spell.rect.colliderect(block.rect):
						HitSound.play()
						spells.remove(spell)
						blocks.remove(block)						
			except: pass
		
		if block.name == 'Beehive':
			try:
				for enemySpell in enemySpells:
					if enemySpell.rect.colliderect(block.rect):
						HitSound.play()
						for enemy in enemies:
							enemy.life -= .8
						
				
			except:
				pass
		
	# Your Projectiles
	for spell in spells:
		spell.move()
		spell.updateRect()
		spell.render()
		if spell.time <= 0:
			spells.remove(spell)
			
	# Move enemies, render them, have them attack, etc	
	for enemySpell in enemySpells:
		enemySpell.move()
		enemySpell.render()
		try:
			if enemySpell.rect.colliderect(player.rect):
				player.gotHit()
				HitSound.play()
				try:
					images.pop()
				except: getRGB(player.in_level)
				enemySpells.remove(enemySpell)
			if enemySpell.x < -20 or enemySpell.x > 490:
				enemySpells.remove(enemySpell)			
		except:
			pass
	
	
	health_x = 0
	#for i in images:
	#	screen.blit(i,(health_x, 0))
	#	health_x+=30
		
	for enemy in enemies:
		if not pause:
			enemy.move()
		enemy.render()
		if enemy.rect.colliderect(player.rect):
			player.gotHit()
			try:
				images.pop()
			except: getRGB(player.in_level)
			pygame.display.flip()
				
			
		#Error checking
		try:
			for spell in spells:
				if spell.rect.colliderect(enemy.rect):
					if spell.name == "Rock":
						HitSound.play()
						enemy.life -= 3
					spells.remove(spell)
		except: pass
		
		if enemy.life <= 0 or enemy.y > screen.get_height() + 10:
			enemies.remove(enemy)
			
				
	# For NPCs in game
	
	for npc in npcs:
		if not pause:
			npc.move() #This must be here so that the NPCs get blitted in front of background
		npc.render()
		if npc.rect.colliderect(player.rect):
			BLACK = (0, 0, 0)
			WHITE = (255, 255, 255)
			RED = (255, 0, 0)
			GREEN = (0, 255, 0)
			BLUE = (0, 0, 255)
			myfont = pygame.font.SysFont("Comic Sans MS", 25)
			# apply it to text on a label
			if npc.name == 'Stelio':
				label = myfont.render("Hey, hey, hey, I'm a bear!", 1, WHITE)
				label1 = myfont.render("Super jump press J", 1, WHITE)
				label2 = myfont.render("Rock throw press I", 1, WHITE)
				labelj = myfont.render("Hold spacebar to jump higher.", 1, WHITE)
				labeli = myfont.render("Press Right CTRL to throw rocks.", 1, WHITE)
				pause = True
				NPCcontact = True
				if I == True:
					pygame.draw.rect( screen, BLACK, (99,99,390,40),0)
					screen.blit(labeli, (100, 100))
					pause = False
				if J == True:
					pygame.draw.rect( screen, BLACK, (99,99,380,40),0)
					screen.blit(labelj, (100, 100))
					pause = False
			elif npc.name == 'Cub':
				label5 = myfont.render("I coulda escaped on my own", 1, WHITE)
				label6 = myfont.render("of course...", 1, WHITE)
				label7 = myfont.render("but, um you know, thanks for the help.", 1, WHITE)
				screen.blit(label5, (npc.x, npc.y-142))
				screen.blit(label6, (npc.x, npc.y-120))
				screen.blit(label7, (npc.x, npc.y-100))
				
			if pause:
			# put the label object on the screen at point x=100, y=100
				pygame.draw.rect( screen, BLACK, (99,99,301,80),0) #pygame.draw.rect(screen, color, (x,y,width,height), thickness)
				screen.blit(label, (100, 100))
				screen.blit(label1, (100, 120))
				screen.blit(label2, (100, 142))
		if not npc.rect.colliderect(player.rect):
			pause = False 
			
		
		
	if player.HP < 0 or player.y > screen.get_height() + 10:
		getRGB(player.in_level)
	
	
	#textRect.centerx = windowSurface.get_rect().centerx
	#textRect.centery = windowSurface.get_rect().centery
	#colorName = (255,0,0) #red square
	#pygame.draw.rect(screen, colorName, (250,150,250,150), 0)#pygame.draw.rect(screen, color, (x,y,width,height), thickness)
	#pygame.display.flip()	
		
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