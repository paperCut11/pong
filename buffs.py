from random import choice, randint
from tkinter import PhotoImage, NORMAL
from os import sep

from theme import get_random_color

class Buff:
	# Constant object, that store in Buffs.buffs list
	def __init__(self, image, image_duration, effect_duration, func, args=0, repeated=0):
		""" Create object, that represent buff """
		self.image = PhotoImage(file="images"+sep+image)
		self.image_duration = image_duration
		
		self.effect_duration = effect_duration
		
		self.func = func
		self.args = args
		self.repeat = repeated
		
		
class AliveBuff:
	# Object, that currently take part in game (shown or makes effect)
	STATE_POPS_UP = 0
	STATE_ACTIVATED = 1
	STATE_DEAD = 2
	
	def __init__(self, x, y, canva, base_buff):
		
		self.x = x
		self.y = y
		
		self.opts = base_buff
		
		self.id = canva.create_image((x, y), image=self.opts.image, state=NORMAL)
		self.c = canva
		
		self.state = AliveBuff.STATE_POPS_UP
		self.counter = 0
		
	def update(self):
		self.counter += 1
		
		if self.state == AliveBuff.STATE_POPS_UP and \
				self.counter == self.opts.image_duration:
			self.die()
		elif self.state == AliveBuff.STATE_ACTIVATED:
			if self.counter == self.opts.effect_duration:
				self.die()
			elif self.opts.repeat != 0 and \
					self.counter%self.opts.repeat == 0:
				self._call_func()
				

		
	def activate(self, *args):
		# Activate effect taken by buff
		self.c.delete(self.id)
		self.state = AliveBuff.STATE_ACTIVATED
		if self.opts.args == 1:
			self.side = args[0]
		self._call_func()
		
		self.counter = 0
		
			
	def _call_func(self, revert=False):
		if self.opts.args == 0:
			self.opts.func(revert=revert)
		elif self.opts.args == 1:
			self.opts.func(self.side, revert=revert)
		else:
			pass	# Silence is golden...
			
	def die(self):
		if self.state == AliveBuff.STATE_POPS_UP:
			self.c.delete(self.id)
		elif self.state == AliveBuff.STATE_ACTIVATED:
			self._call_func(True)
		self.state = AliveBuff.STATE_DEAD
		

class Buffs:
	# Speed up pod	- DONE
	# Slow down pod	- DONE
	# Blur enemy's side - DONE
	# Change pad size - DONE
	# Speed up ball - MAYBE DEL
	# Change pad's control keys - DONE
	# Change ball size - DONE
	# One-time block at center
	# Timed block behind pod
	# Ball change direction and speed to random
	# "Drunk" ball
	
	def __init__(self, sizes, game):
		
		self.ss = sizes
		self.game = game
		self.c = game.c
		
		self.init_buffs()
		
		self.active_buffs = []
		
		# Maybe save it in Pad class??
		self.l_pad_speed_up = 1
		self.r_pad_speed_up = 1
		
		self.l_pad_rotated = False
		self.r_pad_rotated = False
		
		# Here store ids of black rectangulars, in order to than remove it
		self.blured = [] 
		
		self.l_splash_id = 0
		self.r_splash_id = 0
		
		self.l_pad_h = 1
		self.r_pad_h = 1
		
		
	def update(self, ball_id, ball_side):
		# Add buff to the screen
		if self.freq != 0 and randint(1, self.freq) == 1:
			buff = choice(self.buffs)
			x_coord = randint(0, self.ss.WIDTH*3//5) + self.ss.WIDTH/5
			y_coord = randint(50, int(self.ss.HEIGHT)-50)
			self.active_buffs.append(AliveBuff(x_coord, y_coord, self.c, buff))
			
		# Remove dead
		self.active_buffs = [buff for buff in self.active_buffs if buff.state != AliveBuff.STATE_DEAD]
		
		# Update all
		for buff in self.active_buffs:
			if buff.state == AliveBuff.STATE_POPS_UP and \
					self.c.check_collision(ball_id, buff.id):
				buff.activate(ball_side)
			buff.update()
			
	def desactivate(self):
		""" Clear all buff from game """
		for buff in self.active_buffs:
			buff.die()
		
		self.freq = 0
		
	### It would called when ball enters buffs image zone ###
	
	def speed_up_pad(self, side, revert=False):
		if side == "left":
			self.l_pad_speed_up *= 2 if not revert else 0.5
		elif side == "right":
			self.r_pad_speed_up *= 2 if not revert else 0.5
		
	def slow_down_pad(self, side, revert=False):
		self.speed_up_pad(side, not revert)
			
	def blur(self, side, revert=False):
		""" Blur opponent field """
		if side == "left":
			if not revert:
				rect_id = self.c.create_rectangle(self.ss.WIDTH/2, 0,
												  self.ss.RIGHT_TAB, self.ss.HEIGHT,
												  fill="black")
				self.blured.append(rect_id)
			else:
				rect_id = self.blured.pop(0)
				self.c.delete(rect_id)
		elif side == "right":
			if not revert:
				rect_id = self.c.create_rectangle(self.ss.PAD_W, 0,
												  self.ss.WIDTH/2, self.ss.HEIGHT,
												  fill="black")
				self.blured.append(rect_id)
			else:
				rect_id = self.blured.pop(0)
				self.c.delete(rect_id)
				
	def enlarge(self, side, revert=False):
		""" Make pad bigger """
		scale = 2 if not revert else 0.5
		if side == "left":
			self.c.scale_center(self.game.left_pad.id, 1, scale)
		elif side == "right":
			self.c.scale_center(self.game.right_pad.id, 1, scale)
		
	def shrink(self, side, revert=False):
		""" Opposite to previous """
		self.enlarge(side, not revert)
			
	def ball_small(self, revert=False):
		""" The same for ball """
		if not revert:
			self.ss.BALL_RADIUS /= 2
			self.c.scale_center(self.game.ball.id, 0.5)
		else:
			self.ss.BALL_RADIUS *= 2
			self.c.scale_center(self.game.ball.id, 2)
			
	def ball_big(self, revert=False):
		# Ha-ha, I am genius, again
		self.ball_small(not revert)
		
	def ball_teleport(self, revert=False):
		""" Teleport to radom location without changing speed or direction """
		if not revert:
			self.game.ball.teleport()
			
	def die(self, side, revert=False):
		if not revert:
			if side == "left":
				self.game.win("right")
			else:
				self.game.win("left")
				
	def rotate(self, side, revert=False):
		""" Change controls (Up/Down) for pad in <side> """
		if side == "left":
			self.game.left_pad.rotate_controls()
			self.l_pad_rotated = not self.l_pad_rotated
			if self.l_pad_rotated:
				self.game.theme.pin_color("l_pad", "#327045")
			else:
				self.game.theme.unpin_color("l_pad")
		else:
			self.game.right_pad.rotate_controls()
			self.r_pad_rotated = not self.r_pad_rotated
			if self.r_pad_rotated:
				self.game.theme.pin_color("r_pad", "#327045")
			else:
				self.game.theme.unpin_color("r_pad")
			
	def choose_random_buff(self, side, revert=False):
		if not revert:
			buff = choice(self.buffs)
			a_buff = AliveBuff(0, 0, self.c, buff)
			a_buff.activate(side)
			self.active_buffs.append(a_buff)
			
	def splash(self, side, revert=False):
		def check(side_check, spl_id):
			if side == side_check:
				if revert:
					self.c.delete(spl_id)
					return 0
				elif spl_id == 0:
					new_id = self.c.create_rectangle((0, 0, self.ss.WIDTH/2, self.ss.HEIGHT), fill="white")
					if side == "left":
						self.c.move(new_id, self.ss.WIDTH/2, 0)
					self.c.tag_lower(new_id)
					return new_id
				else:
					self.c.itemconfig(spl_id, fill=get_random_color())
			return spl_id
			
		self.l_splash_id = check("left", self.l_splash_id)
		self.r_splash_id = check("right", self.r_splash_id)

	def init_buffs(self):
		
		buffs_1 = ( ("green.png", 180, 100, self.speed_up_pad, 1),
					("red.png", 180, 100, self.slow_down_pad, 1),
					("enlarge.png", 140, 90, self.enlarge, 1),
					("shrink.png", 140, 90, self.shrink, 1) )
					   	
		buffs_2 = ( ("ball_red.png", 200, 130, self.ball_small),
					("ball_green.png", 200, 130, self.ball_big),
					("question.png", 200, 1, self.choose_random_buff, 1) )
		
		buffs_3 = ( ("teleport.png", 200, 1, self.ball_teleport),
					#("blur.png", 180, 50, self.blur, 1),	Not shown in some themes ☹️
					("splashes.png", 150, 200, self.splash, 1, 10),
					("rotate.png", 200, 100, self.rotate, 1),  # how to make it more visible????
					("die2.png", 100, 1, self.die, 1) ) 
		
		if self.game.CRAZY.it == 0:
			self.freq = 0
			buff_list = []
		elif self.game.CRAZY.it == 1:
			self.freq = 250
			buff_list = buffs_1
		elif self.game.CRAZY.it == 2:
			self.freq = 100
			buff_list = buffs_1 + buffs_2
		elif self.game.CRAZY.it == 3 or self.game.CRAZY.it == 4:
			self.freq = 10
			buff_list = buffs_1 + buffs_2 + buffs_3
			
		self.buffs = [Buff(*arg) for arg in buff_list]


		
