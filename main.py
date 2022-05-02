import pygame
import sys
from pygame import Vector2 as vector2
import json
import os

pygame.init()

screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size, vsync=True)
friction = 0.03
drag = 0.06
car_power = 0.2
zoom = 1
traction = 1.5


def handle_events():
	keys = {'left': False, 'right': False, 'up': False, 'down': False, "reset": False, 'brake': False, 'load_next': False}
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_l:
				keys['load_next'] = True
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

class map:
	def __init__(self):
		self.loaded_map = 0
		self.list_of_turns = []
		self.list_of_lines = self.calc_lines(self.list_of_turns, 80)
		self.wall1, self.wall2 = self.colide_lines(*self.list_of_lines)
		self.load_next_map(zoom)

	def load_next_map(self, zoom):
		width = 80*zoom
		temp = self.load_from_json(self.loaded_map + 1)
		if temp != "too large" and temp != "File does not exist":
			self.list_of_turns = temp
			self.loaded_map += 1
		else:
			if self.loaded_map != 0:
				print("Map " + str(self.loaded_map + 1) + " does not exist.")
				self.loaded_map = 0
				self.list_of_turns = self.load_from_json(self.loaded_map + 1)
				self.loaded_map += 1
			else:
				print("Map " + str(self.loaded_map + 1) + " does not exist.", end=" ")
				print("No Map Are Made")
				loaded_map = 0
		for x in range(len(self.list_of_turns)):
			self.list_of_turns[x] = (self.list_of_turns[x][0] * zoom, self.list_of_turns[x][1] * zoom)
		if self.list_of_turns:
			self.list_of_lines = self.calc_lines(self.list_of_turns, width)
			self.wall1, self.wall2 = self.colide_lines(*self.list_of_lines)

	def calc_lines(self,list_of_points, road_width):
		lines1 = []
		lines2 = []
		for i in range(len(list_of_points)):
			if i == len(list_of_points) - 1:
				i = -1
			temp = ((vector2(list_of_points[i + 1]) - vector2(list_of_points[i])).normalize()).rotate(
				90) * road_width / 2
			point1 = vector2(list_of_points[i]) + temp
			point2 = vector2(list_of_points[i + 1]) + temp
			lines1.append((point1, point2))
			temp = ((vector2(list_of_points[i + 1]) - vector2(list_of_points[i])).normalize()).rotate(
				-90) * road_width / 2
			point1 = vector2(list_of_points[i]) + temp
			point2 = vector2(list_of_points[i + 1]) + temp
			lines2.append((point1, point2))
		return lines1, lines2

	def colide_lines(self,lines1, lines2):
		point_in = []
		for x in range(len(lines1)):
			if x == len(lines1) - 1:
				x = -1
			x1 = lines1[x][0].x
			x2 = lines1[x][1].x
			y1 = lines1[x][0].y
			y2 = lines1[x][1].y
			x3 = lines1[x + 1][0].x
			x4 = lines1[x + 1][1].x
			y3 = lines1[x + 1][0].y
			y4 = lines1[x + 1][1].y
			dnom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
			if dnom == 0:
				continue
			point_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / dnom
			point_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / dnom
			point_in.append(vector2(point_x, point_y))
		point_out = []
		for x in range(len(lines2)):
			if x == len(lines2) - 1:
				x = -1
			x1 = lines2[x][0].x
			x2 = lines2[x][1].x
			y1 = lines2[x][0].y
			y2 = lines2[x][1].y
			x3 = lines2[x + 1][0].x
			x4 = lines2[x + 1][1].x
			y3 = lines2[x + 1][0].y
			y4 = lines2[x + 1][1].y
			dnom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
			if dnom == 0:
				continue
			point_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / dnom
			point_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / dnom
			point_out.append(vector2(point_x, point_y))
		return point_in, point_out

	def draw(self,wall1, wall2, screen):
		if len(wall1) >= 2 and len(wall2) >= 2:
			pygame.draw.polygon(screen, (0,0,0), wall1, 3)
			pygame.draw.polygon(screen, (0,0,0), wall2, 3)

	def load_from_json(self,file_num):
		print("Loading map" + str(file_num))
		list_of_files = os.listdir("maps")
		largest_number = 0
		for x in list_of_files:
			try:
				num = int((x.split(".")[0]).split('map')[-1])
				largest_number = max(largest_number, num)
			except:
				continue
		if file_num > largest_number:
			return "too large"
		elif file_num < 1:
			return "File does not exist"
		elif "map" + str(file_num) + ".json" in list_of_files:
			file = open("maps/map" + str(file_num) + ".json", "rt")
			return json.loads(file.read())
		else:
			return "File does not exist"

class car:
	def __init__(self, x, y, stearing, angle):
		self.pos = pygame.Vector2(x, y)
		self.size = pygame.Vector2(25, 12) * zoom
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
		if self.speed >= friction:
			self.speed -= friction
		elif self.speed <= -friction:
			self.speed += friction
		self.speed *= (1 - drag)
		if self.speed <= 0.01 and self.speed >= -0.01:
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


mycar = car(500, 300, 30, 180)
clock = pygame.time.Clock()
# map = pygame.image.load('map.png')
# map = pygame.transform.scale(map,(800,600))
Map = map()

while True:
	clock.tick(60)
	screen.fill((100, 100, 100))
	Map.draw(Map.wall1,Map.wall2,screen)
	# screen.blit(map,(0,0))
	keys = handle_events()
	if keys['reset']:
		mycar = car(500, 300, 30, 180)
	if keys['load_next']:
		Map.load_next_map(zoom)

	# print(keys)
	mycar.draw(screen)
	mycar.update(keys)
	pygame.display.flip()
