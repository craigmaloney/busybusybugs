#!/usr/bin/env python

# Busy Busy Bugs
# Written by Craig Maloney
# (c) 2007 Craig Maloney
# Portions of this program come from the excellent gamelet
# Particle Invaders! by Chuck Arellano
# http://www.scriptedfun.com
# Written for the PyWeek #4 challenge
# Released under the GPL version 2 license

import os, sys
import pygame, random
from pygame.locals import *
import data

SCREENRECT = Rect(0,0,800,600)
MARGINBOTTOM = 16
MARGINSIDES = 32
BLACK = (0, 0, 0)

class Clay_Pot(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.rect = self.image.get_rect(midtop = pos)

class Flower_head(pygame.sprite.Sprite):
	def __init__(self,pos):
		self.position = pos
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.rect = self.image.get_rect(center = pos)
	def update(self):
		self.rect.center=self.position
	def set_position(self,pos):
		self.position = pos

class Leaf(pygame.sprite.Sprite):
	def __init__(self,pos):
		self.position = pos
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.rect = self.image.get_rect(center = pos)
	def update(self):
		self.rect.center=self.position
	def drop(self):
		(x,y) = self.position
		y=y-5
		self.position = (x,y)

class Flower(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.position = pos
		self.size=250
		self.image = pygame.Surface([30,self.size])
		self.image.fill([0,255,60])
		self.rect = self.image.get_rect()
		self.rect.midbottom = (self.position)
		self.sound = Flower.sound
		self.head = Flower_head(self.rect.midtop)
		self.leaves=[]
		self.leaves.append(Leaf((self.rect.bottomleft)))
		self.leaves.append(Leaf((self.rect.bottomright)))
		self.pot = Clay_Pot(self.rect.midbottom)
		self.last_growing = 0
	def update(self):
		if (self.size) :
			self.image = pygame.Surface([30,self.size])
			self.image.fill([0,255,60])
			self.rect = self.image.get_rect()
			self.rect.midbottom = (self.position)
			self.head.set_position(self.rect.midtop)
			if (self.last_growing > 0):
				self.last_growing = self.last_growing - 1
		else:
			self.head.kill()
			self.kill()
	def sucking(self):
		if (self.size > 0):
			self.size=self.size-5
			self.sound.play()
	def growing(self):
		if ((self.size > 0 and self.size <= 250) and self.last_growing <= 0): 
			self.last_growing=10
			self.size=self.size+10
			self.sound.play()
	def get_position(self):
		return self.rect.center
	def is_alive(self):
		if self.size <= 0:
			return False
		else:
			return True
class Bee(pygame.sprite.Sprite):
	def __init__ (self,pos):
		pygame.sprite.Sprite.__init__(self,self.containers)
		self.rect = self.image.get_rect(center = pos)
		self.alive = True
		self.sound = Bee.sound
		self.speed = 4
	def update(self):
		self.rect.move_ip(self.speed, random.randrange(-3,5))

		if (self.rect.left > SCREENRECT.right): 
			self.kill()

	def runaway(self):
		# No! Bad Player!
		if (self.alive):
			self.alive = False
			self.sound.play()
			self.speed=20
	def is_alive(self):
		return self.alive

class Bug(pygame.sprite.Sprite):
	def __init__ (self,pos,flower):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.flower = flower
		self.rect = self.image.get_rect(center = pos)
		(self.destx,self.desty) = self.flower.get_position()
		self.dx = random.randrange(10)
		self.dy = random.randrange(20)
		self.frame = 0
		self.attack = False
		self.done = False
		self.last_change = 0
		self.change_times = 0
		self.suck_frames = 0
		self.sounds = Bug.sounds

	def update(self):
		self.rect.move_ip(self.dx, self.dy)
		x = self.rect.centerx
		y = self.rect.centery
		self.last_change = self.last_change + 1
		if (x>self.destx):
			self.dx= (self.dx - 1) 
		if (x<self.destx):
			self.dx = (self.dx + 1) 
		if (y>self.desty):
			self.dy= (self.dy - 1) 
		if (y<self.desty):
			self.dy = (self.dy + 1) 
		if (self.last_change > 100 and self.attack == False):
			self.attack = True
		if (random.randrange(100) == 10):
			self.attack = True
		if (self.attack and not self.done):
			if (self.last_change > 10):
				# Zero in on the target
				self.dy = self.dy * .5
				self.dx = self.dx * .5
				self.last_change = 0
				self.change_times = self.change_times + 1
			if (abs(self.dx) <1 and abs(self.dy) <1):
				self.flower.sucking()
				self.dx = 0
				self.dy = 0
				self.suck_frames = self.suck_frames + 1
			if (self.suck_frames > 5 or self.change_times > 30):
				self.success()
		if (self.done and (self.rect.left > SCREENRECT.right or
			 self.rect.top > SCREENRECT.bottom)):
			self.kill()
		if (not (self.done) and self.flower.is_alive() == False):
			self.success()

	def runaway(self,score):
		# COUGH! Run AWAY!
		if (not self.done):
			self.done = True
			self.sounds[0].play()
			self.destx = (SCREENRECT.right + 200)
			self.desty = SCREENRECT.bottom
			score.add_score(10)
	def success(self):
		# Success! Run away laughing!
		self.sounds[1].play()
		self.destx = (SCREENRECT.right + 200)
		self.desty = SCREENRECT.top
		self.attack = False
		self.done = True

				
class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.unfire()
		self.rect = self.image.get_rect(bottom = SCREENRECT.height - MARGINBOTTOM)
		self.sprays_left = 0
		self.sound = Player.sound
	def update(self):
		x, y = pygame.mouse.get_pos()
		x = min(max(x, MARGINSIDES), SCREENRECT.width - MARGINSIDES)
		y = min(max(y, MARGINBOTTOM), SCREENRECT.height - MARGINBOTTOM)
		self.rect.midtop = (x,y)
		if (self.fireon and self.sprays_left > 0):
			if self.delay > 0:
				self.delay = self.delay - 1
			else:
				self.delay = 10
				self.sound.play()
				for i in (range(0,32)):
					offsetx = random.randrange(-48,48)
					offsety = random.randrange(-48,48)

					(coordx,coordy) = (self.rect.midtop)
					coordx = coordx + offsetx
					coordy = coordy + offsety

					Spray((coordx,coordy))
				self.sprays_left = self.sprays_left - 1

	def fire(self):
		self.fireon = True

	def unfire(self):
		self.delay = 0
		self.fireon = False

	def spray_replenish(self,amount):
		self.sprays_left = self.sprays_left + amount
		if self.sprays_left > 30:
			self.sprays_left = 30

	def spray_new_can(self):
		self.sprays_left = 15

	def get_spray_count(self):
		return self.sprays_left

def spray_image():
	image = pygame.Surface((25,25),SRCALPHA)
	image.fill((200,200,200))
	#pygame.draw.circle(image, (200,200,200),(50,50),50)
	#return image.convert_alpha()
	return image.convert()

class Spray(pygame.sprite.Sprite):
	def __init__(self,pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.rect = self.image.get_rect(center = pos)
		self.alpha = 200
	def update(self):
		self.alpha = self.alpha - 10
		self.image.set_alpha(self.alpha)
		if (self.alpha < 0):
			self.kill()

class Levels:
	def __init__(self):
		self.level = 0
		self.attackers = [10,10,15,15,20,20,25,25,25,30,30,30,35,35,35,40,40,40,50,60]
		self.attacker_last_time = [30,30,25,25,20,20,20,15,15,15,10,10,10,5,5,5,3,3,3,5]
	def get_level(self):
		return (self.level+1,
			self.attackers[min(self.level,len(self.attackers)-1)],
			self.attacker_last_time[min(self.level,len(self.attacker_last_time)-1)])
	def restart_game(self):
		self.level = 0
	def next_level(self):
		self.level = self.level + 1

class Score(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self,self.containers)
		self.font = pygame.font.Font(data.filepath('fonts','BOYZRGRO.TTF'),36)
		self.image = pygame.Surface([200,26])
		self.rect = self.image.get_rect()
		self.rect.topleft = (500,2)
		self.score = 0
	def update(self):
		text = "Score: %06d" % self.score
		self.image = self.font.render(text,1,(0,0,0))
		self.rect = self.image.get_rect()
		self.rect.topleft = (500,2)
	def add_score(self,additional):
		self.score = self.score + additional
	def get_score(self):
		return self.score

class Spray_gauge(pygame.sprite.Sprite):
	def __init__(self,player):
		pygame.sprite.Sprite.__init__(self,self.containers)
		self.font = pygame.font.Font(data.filepath('fonts','BOYZRGRO.TTF'),36)
		self.image = pygame.Surface([200,26])
		self.rect = self.image.get_rect()
		self.rect.topleft = (200,2)
		self.player = player
	def update(self):
		sprays = self.player.get_spray_count()
		text = "Sprays x %02d" % sprays
		self.image = self.font.render(text,1,(0,0,0))
		self.rect = self.image.get_rect()
		self.rect.topleft = (200,2)

class Status(pygame.sprite.Sprite):
	def __init__(self,text):
		pygame.sprite.Sprite.__init__(self,self.containers)
		self.font = pygame.font.Font(data.filepath('fonts','BOYZRGRO.TTF'),72)
		self.image = pygame.Surface([200,26])
		self.rect = self.image.get_rect()
		self.text = text
		self.image = self.font.render(self.text,1,(0,0,0))
		self.rect = self.image.get_rect()
		self.rect.topright = (0,500)
	def update(self):
		self.rect.move_ip(10,0)
		if self.rect.left > SCREENRECT.right:
			self.kill()

class Title(pygame.sprite.Sprite):
	def __init__(self,text,color):
		pygame.sprite.Sprite.__init__(self,self.containers)
		self.font = pygame.font.Font(data.filepath('fonts','BOYZRGRO.TTF'),90)
		self.image = pygame.Surface([200,26])
		self.rect = self.image.get_rect()
		self.text = text
		self.image = self.font.render(self.text,1,color)
		self.rect = self.image.get_rect()
		self.rect.center = (SCREENRECT.center)
	def update(self):
		(x,y) = SCREENRECT.center
		offx = random.randrange(-2,4)
		offy = random.randrange(-2,4)
		self.rect.center = (x+offx,y+offy)


def kill_all_objects(object):
	for i in object:
		i.kill()

def game():
	pygame.mixer.pre_init(44100,8,4,1024)
	pygame.init()
	pygame.font.init()
	pygame.mixer.music.set_volume(2.0)
	if pygame.mixer.music.get_busy():
		pass
	else:
		musicfile = data.filepath('midi','bumblbee.mid')
		pygame.mixer.music.load(musicfile)
		pygame.mixer.music.play(-1)
	#screen = pygame.display.set_mode(SCREENRECT.size,FULLSCREEN|DOUBLEBUF|HWSURFACE)
	screen = pygame.display.set_mode(SCREENRECT.size,DOUBLEBUF|HWSURFACE)
	clock = pygame.time.Clock()
	background = pygame.image.load(data.filepath('images','new_background.png')).convert()
	#text_font = pygame.font.Font(data.filepath('fonts','BOYZRGRO.TTF'),26)

	clay_pots = pygame.sprite.Group()
	bugs = pygame.sprite.Group()
	bees = pygame.sprite.Group()
	flowers = pygame.sprite.Group()
	flower_heads = pygame.sprite.Group()
	player = pygame.sprite.Group()
	leaves = pygame.sprite.Group()
	spray = pygame.sprite.Group()
	score = pygame.sprite.Group()
	spray_gauge = pygame.sprite.Group()
	status = pygame.sprite.Group()
	title = pygame.sprite.Group()
	all = pygame.sprite.OrderedUpdates()

	Flower.containers = all, flowers
	Bug.containers = all, bugs
	Bee.containers = all, bees
	Clay_Pot.containers = all
	Flower_head.containers = all, flower_heads
	Player.containers = all
	Score.containers = all
	Status.containers = all
	Leaf.containers = all
	Spray_gauge.containers = all
	Spray.containers = all, spray
	Title.containers = all

	# Load Images
	Bug.image = pygame.image.load(data.filepath('images','bug.png'))
	Clay_Pot.image = pygame.image.load(data.filepath('images','clay_pot.png'))
	Flower_head.image = pygame.image.load(data.filepath('images','flower_head.png'))
	Player.image = pygame.image.load(data.filepath('images','spraycan.png'))
	Bee.image = pygame.image.load(data.filepath('images','bee.png'))
	Leaf.image = pygame.image.load(data.filepath('images','leaf.png'))
	Spray.image = spray_image()


	# Load Sounds
	Bug.sounds = [pygame.mixer.Sound(data.filepath('sounds','cough.wav')), pygame.mixer.Sound(data.filepath('sounds','laugh.wav'))]
	Player.sound = pygame.mixer.Sound(data.filepath('sounds','spray.wav'))
	Bee.sound = pygame.mixer.Sound(data.filepath('sounds','yuck.wav'))
	Flower.sound = pygame.mixer.Sound(data.filepath('sounds','flower_suck.wav'))


	screen.blit(background,(0,0))
	flower_objects = []
	flower_list = []
	pygame.display.flip()
	attacker_last = 0
	level = Levels()
	game = False
	start_new_game = False
	status_pause = 0
	last_score = 0
	first_time = True
	flag = True

	while 1:
		status_pause = status_pause + 1
		if (first_time):
			title_text = "Busy Busy Bugs"
			Title(title_text,(0,0,0))
			Title(title_text,(255,0,0))
			Title(title_text,(0,255,255))
			Title(title_text,(0,255,0))
			Title(title_text,(0,0,255))
			first_time = False
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				start_new_game = True
			if event.type == KEYDOWN:
				if ((event.key <> 27) and (event.key <> 113)):
					start_new_game = True
				else:
					sys.exit()

		if status_pause > 100:
			flag = not flag
			if (flag):
				status = Status ("Press any key to start...")
			else:
				status = Status ("Last score: %06d" % last_score)
			status_pause = 0
		all.clear(screen,background)
		all.update()
		dirty = all.draw(screen)
		pygame.display.update(dirty)
		clock.tick(30)

		if (start_new_game) :
			kill_all_objects(all)
			for i in (range(100,SCREENRECT.right,300)):
				flower_objects.append(Flower((i,350)))
			player = Player()
			level.restart_game()
			game = True
			playing = True
			score = Score()
			spray_gauge = Spray_gauge(player)
			pygame.event.clear()

			

		while game:
			# Get the Level Specifics
			(current_level,attackers, attacker_last_time) = level.get_level()
			max_bee_chance = attackers / 2
			playing = True
			status = Status("Level %2d" % current_level)
			start_pause = 100
			bee_chance = 0
			bee_upset = False

			# Find the flowers that are still alive
			flower_list = []
			for flower in flower_objects:
				if flower.is_alive():
					flower_list.append(flower)
					 
			# Are there any flowers that are still alive?
			if (len(flower_list) < 1):
				# Game over, man, game over
				playing = False
				game = False
				player.kill()
				last_score = score.get_score()
				kill_all_objects(all)
				start_new_game = False
				first_time = True
			else:
				# Player gets 5 sprays for each live flower
				player.spray_replenish(len(flower_list)*5)
			
			while playing:
				for event in pygame.event.get():
					if event.type == QUIT:
						sys.exit()
					if event.type == MOUSEBUTTONDOWN:
						player.fire()
					if event.type == MOUSEBUTTONUP:
						player.unfire()
					if event.type == KEYDOWN:
						if event.key == 27 or event.key == 113:
							# Quit the game
							playing = False
							game = False
							start_new_game = False
							first_time = True
							kill_all_objects(all)

				if ((attackers > 0 and attacker_last > attacker_last_time) and start_pause <= 0 ):
					flowernum = random.randrange(len(flower_list))
					random_entry = random.randrange(0,2)
					random_entry = random_entry * SCREENRECT.right
					Bug((random_entry,0),flower_list[flowernum])
					attackers = attackers - 1
					attacker_last = 0
					bee_chance = bee_chance + 1
				attacker_last = attacker_last + 1
				if ((current_level >= 3) and (bee_chance >= max_bee_chance) and not bee_upset) :
					Bee((0,random.randrange(100,200)))
					bee_chance = 0
				for bug in (pygame.sprite.groupcollide(bugs,spray,False, False)):
					bug.runaway(score)
				for bee in (pygame.sprite.groupcollide(bees,spray,False,False)):
					bee.runaway()
					bee_upset = True
				bee_flower_collide = pygame.sprite.groupcollide(bees,flowers,False,False)
				if (bee_flower_collide) :
					for bee in (bee_flower_collide):
						if bee.is_alive():
							[flower] = bee_flower_collide[bee]
							flower.growing()


				if (attackers <= 0 and (not (bugs.sprites()))):
					playing = False
				all.clear(screen,background)
				all.update()
				dirty = all.draw(screen)
				pygame.display.update(dirty)
				clock.tick(30)
				start_pause = start_pause - 1
			level.next_level()
def main():
	game()
	sys.exit()

if __name__ == '__main__':
	main()
