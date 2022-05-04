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

def lineLine(x1, y1, x2, y2, x3, y3, x4, y4):
	dnom = ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
	if dnom == 0:
		return False
	uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / dnom
	uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / dnom
	if (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1):
		# intersectionX = x1 + (uA * (x2 - x1))
		# intersectionY = y1 + (uA * (y2 - y1))
		# pygame.draw.circle(screen, (255, 0, 0), (int(intersectionX), int(intersectionY)), 5)
		return True

def lineRect(P1, P2, FL, FR, BR, BL):
	left = lineLine(*P1, *P2 , *FL, *BL)
	right = lineLine(*P1, *P2 ,*FR,*BR)
	front = lineLine(*P1, *P2 ,*FL,*FR)
	back = lineLine(*P1, *P2 ,*BL,*BR)
	if left or right or front or back:
		return True
	return False

class map:
	def __init__(self):
		self.loaded_map = 0
		self.list_of_turns = []
		self.list_of_lines = self.calc_lines(self.list_of_turns, 80)
		self.wall1, self.wall2 = self.colide_lines(*self.list_of_lines)
		self.checkpoints = []
		self.load_next_map(zoom)

	def get_checkpoints(self):
		self.checkpoints = []
		for x in range(len(self.wall1)):
			self.checkpoints.append((self.wall1[x],self.wall2[x]))

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
			self.startangle = (vector2(self.list_of_turns[2]) - vector2(self.list_of_turns[1])).normalize().as_polar()[1]
			self.startpos = vector2(self.list_of_turns[1])

		self.get_checkpoints()

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

	def draw(self,wall1, wall2, screen, checkpoint = []):
		if len(wall1) >= 2 and len(wall2) >= 2:
			pygame.draw.polygon(screen, (0,0,0), wall1, 3)
			pygame.draw.polygon(screen, (0,0,0), wall2, 3)
		if len(wall1) > 0 and len(wall2) > 0:
			pygame.draw.line(screen, (255, 0, 0), wall1[0], wall2[0], 3)

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
		self.corners = {'FL': None, 'FR': None, 'BR': None, 'BL': None}
		self.checkpoints_got = set([0])
		self.laps = 0
		self.update_corners()

	def update_corners(self):
		self.corners = {'FL': None, 'FR': None, 'BR': None, 'BL': None, 'order': ['FL','FR','BR','BL']}
		self.corners['FL'] = (self.pos + pygame.Vector2(self.size.x / 2, -self.size.y / 2).rotate(-self.angle))
		self.corners['FR'] = (self.pos + pygame.Vector2(self.size.x / 2, self.size.y / 2).rotate(-self.angle))
		self.corners['BR'] = (self.pos + pygame.Vector2(-self.size.x / 2, self.size.y / 2).rotate(-self.angle))
		self.corners['BL'] = (self.pos + pygame.Vector2(-self.size.x / 2, -self.size.y / 2).rotate(-self.angle))
	
	def draw(self, screen):
		tempsurf = pygame.transform.rotate(self.carbody, self.angle)
		screen.blit(tempsurf, self.pos - pygame.Vector2(tempsurf.get_rect().size) / 2)
		for x in self.corners['order']:
			pygame.draw.circle(screen, (255,0,255), self.corners[x], 3)
	
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

		self.update_corners()

	def calcwheel(self):
		dir = self.dir
		front_wheel = self.pos + dir * self.size.x * 0.4
		back_wheel = self.pos - dir * self.size.x * 0.4
		return front_wheel, back_wheel

	def collide(self, wall1, wall2, screen):
		for x in range(len(wall1)):
			if wall1[x-1] != wall1[x]:
				if lineRect(wall1[x-1], wall1[x], self.corners['FL'],self.corners['FR'],self.corners['BR'],self.corners['BL']):
					if self.speed > 0:
						self.speed = -3
					else:
						self.speed = 3
					return
		for x in range(len(wall2)):
			if wall2[x - 1] != wall2[x]:
				if lineRect(wall2[x-1], wall2[x], self.corners['FL'],self.corners['FR'],self.corners['BR'],self.corners['BL']):
					if self.speed > 0:
						self.speed = -3
					else:
						self.speed = 3
					return


	def collide_checkpoint(self,screen,checkpoints):

		for x in range(len(checkpoints)):

			if lineRect(checkpoints[x][0],checkpoints[x][1],self.corners['FL'],self.corners['FR'],self.corners['BR'],self.corners['BL']):
				if (x-1)%len(checkpoints) in self.checkpoints_got:
					if x == 0:
						self.laps += 1
						self.checkpoints_got = {0}
						print('lap done')
					self.checkpoints_got.add(x)


Map = map()
mycar = car(*Map.startpos.xy, 20, Map.startangle)
clock = pygame.time.Clock()
# map = pygame.image.load('map.png')
# map = pygame.transform.scale(map,(800,600))

while True:
	clock.tick(60)
	screen.fill((100, 100, 100))
	Map.draw(Map.wall1,Map.wall2,screen)
	# screen.blit(map,(0,0))
	keys = handle_events()
	if keys['reset']:
		mycar = car(*Map.startpos.xy, 20, Map.startangle)
	if keys['load_next']:
		Map.load_next_map(zoom)
		mycar = car(*Map.startpos.xy, 20, Map.startangle)

	# print(keys)
	mycar.draw(screen)
	mycar.update(keys)
	mycar.collide_checkpoint(screen, Map.checkpoints)
	mycar.collide(Map.wall1,Map.wall2,screen)
	pygame.display.flip()
