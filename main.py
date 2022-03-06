import pygame
import sys
import math

pygame.init()

screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size, vsync=True)
friction = 0.95
car_power = 0.6
zoom = 0.5
traction = 1.5


def handle_events():
	keys = {'left': False, 'right': False, 'up': False, 'down': False, "reset": False, 'brake': False}
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	pygame_keys = pygame.key.get_pressed()
	if pygame_keys[pygame.K_LEFT] or pygame_keys[pygame.K_a]:
		keys['left'] = True
	if pygame_keys[pygame.K_RIGHT] or pygame_keys[pygame.K_d]:
		keys['right'] = True
	if pygame_keys[pygame.K_UP] or pygame_keys[pygame.K_w]:
		keys['up'] = True
	if pygame_keys[pygame.K_DOWN] or pygame_keys[pygame.K_s]:
		keys['down'] = True
	if pygame_keys[pygame.K_r]:
		keys['reset'] = True
	if pygame_keys[pygame.K_SPACE]:
		keys['brake'] = True
	return keys


class car:
	def __init__(self, x, y, stearing, angle):
		self.pos = pygame.Vector2(x, y)
		self.size = pygame.Vector2(100, 50) * zoom
		self.angle = angle
		self.speed = 0
		self.dir = pygame.Vector2(1, 0).rotate(self.angle)
		self.stearing = stearing
		self.carbody = pygame.image.load('carbody.png')
		self.carbody = pygame.transform.scale(self.carbody, (int(self.size.x), int(self.size.y)))
		self.acceleration = 0.0
	
	def draw(self, screen):
		tempsurf = pygame.transform.rotate(self.carbody, self.angle)
		screen.blit(tempsurf, self.pos - pygame.Vector2(tempsurf.get_rect().size) / 2)
	
	def update(self, keys):
		self.acceleration = 0.0
		if keys['brake']:
			self.speed *= 0.9
		else:
			if keys['up']:
				self.acceleration = car_power * zoom
			if keys['down']:
				self.acceleration = -car_power * zoom
		self.speed += self.acceleration
		self.speed *= friction
		if self.speed < 0.01 and self.speed > -0.01:
			self.speed = 0
		
		current_steering = 0
		if keys['left']:
			current_steering -= self.stearing
		if keys['right']:
			current_steering += self.stearing
		front_wheel, back_wheel = self.calcwheel()
		# print(front_wheel)
		back_wheel = back_wheel + self.speed * self.dir
		# print(current_steering)
		temp = pygame.Vector2(front_wheel)
		front_wheel += pygame.Vector2(self.dir).rotate(current_steering).normalize() * self.speed
		# print(front_wheel - temp if front_wheel - temp != 0 else "", end="")
		dir = front_wheel - back_wheel
		if self.speed > 20:
			self.dir = self.dir.lerp(dir.normalize(), 0.5)
		else:
			self.dir = self.dir.lerp(dir.normalize(), 0.9)
		self.pos = (front_wheel + back_wheel) / 2
		self.angle = -dir.as_polar()[1]
		
		# pygame.draw.circle(screen, (255, 0, 0), self.pos, 5)
		# pygame.draw.circle(screen, (0, 255, 0), front_wheel, 5)
		# pygame.draw.circle(screen, (0, 0, 255), back_wheel, 5)
	
	def rotateAnim(self):
		self.angle += 1
		pygame.draw.circle(screen, (255, 0, 0), self.pos, 5)
	
	def calcwheel(self):
		dir = self.dir
		front_wheel = self.pos + dir * self.size.x * 0.4
		back_wheel = self.pos - dir * self.size.x * 0.4
		return front_wheel, back_wheel


mycar = car(500, 300, 20, 180)
clock = pygame.time.Clock()

while True:
	clock.tick(60)
	screen.fill((100, 100, 100))
	keys = handle_events()
	if keys['reset']:
		mycar = car(500, 300, 30, 180)
	# print(keys)
	mycar.draw(screen)
	mycar.update(keys)
	pygame.display.flip()
