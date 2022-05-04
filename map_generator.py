import pygame
from pygame import Vector2 as vector2
import json
import os

def calc_lines(list_of_points,road_width):
	lines1 = []
	lines2 = []
	for i in range(len(list_of_points)):
		if i == len(list_of_points)-1:
			i = -1
		temp = ((vector2(list_of_points[i+1])-vector2(list_of_points[i])).normalize()).rotate(90)*road_width/2
		point1 = vector2(list_of_points[i])+temp
		point2 = vector2(list_of_points[i+1])+temp
		lines1.append((point1,point2))
		temp = ((vector2(list_of_points[i+1])-vector2(list_of_points[i])).normalize()).rotate(-90)*road_width/2
		point1 = vector2(list_of_points[i])+temp
		point2 = vector2(list_of_points[i+1])+temp
		lines2.append((point1,point2))
	return lines1,lines2

def colide_lines(lines1, lines2):
	point_in = []
	for x in range(len(lines1)):
		if x == len(lines1)-1:
			x = -1
		x1 = lines1[x][0].x
		x2 = lines1[x][1].x
		y1 = lines1[x][0].y
		y2 = lines1[x][1].y
		x3 = lines1[x+1][0].x
		x4 = lines1[x+1][1].x
		y3 = lines1[x+1][0].y
		y4 = lines1[x+1][1].y
		dnom = (x1 - x2) * (y3-y4)-(y1-y2)*(x3-x4)
		if dnom == 0:
			continue
		point_x = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/dnom
		point_y = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/dnom
		point_in.append(vector2(point_x,point_y))
	point_out = []
	for x in range(len(lines2)):
		if x == len(lines2)-1:
			x = -1
		x1 = lines2[x][0].x
		x2 = lines2[x][1].x
		y1 = lines2[x][0].y
		y2 = lines2[x][1].y
		x3 = lines2[x+1][0].x
		x4 = lines2[x+1][1].x
		y3 = lines2[x+1][0].y
		y4 = lines2[x+1][1].y
		dnom = (x1 - x2) * (y3-y4)-(y1-y2)*(x3-x4)
		if dnom == 0:
			continue
		point_x = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/dnom
		point_y = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/dnom
		point_out.append(vector2(point_x,point_y))
	return point_in,point_out
		
def draw(wall1, wall2, screen):
	if len(wall1) >= 2 and len(wall2) >= 2:
		pygame.draw.polygon(screen, (255,255,255), wall1, 3)
		pygame.draw.polygon(screen, (255,255,255), wall2, 3)
	if len(wall1)>0 and len(wall2) >0:
		pygame.draw.line(screen, (255, 0, 0), wall1[0], wall2[0], 3)
		
def save_to_json(list_of_turns):
	list_of_files = os.listdir("maps")
	largest_number = 0
	for x in list_of_files:
		try:
			num = int((x.split(".")[0]).split('map')[-1])
			largest_number = max(largest_number,num)
		except:
			continue
	file = open("maps/map"+str(largest_number+1)+".json","wt")
	file.write(json.dumps(list_of_turns))
	
def load_from_json(file_num):
	print("Loading map"+str(file_num))
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
	elif "map"+str(file_num)+".json" in list_of_files:
		file = open("maps/map"+str(file_num)+".json","rt")
		return json.loads(file.read())
	else:
		return "File does not exist"
	
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Map Generator")

list_of_turns = []
list_of_lines = calc_lines(list_of_turns,80)
wall1, wall2 = colide_lines(*list_of_lines)
selected_point = -1
loaded_map = 0

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT or event.key == pygame.K_a:
				selected_point -= 1
				if selected_point < 0:
					selected_point = len(list_of_turns)-1
			if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
				selected_point += 1
				if selected_point > len(list_of_turns)-1:
					selected_point = 0
					
			#add saving the map
			if event.key == pygame.K_s:
				print("Saving map")
				save_to_json(list_of_turns)
				
			#load a map
			if event.key == pygame.K_l:
				temp = load_from_json(loaded_map+1)
				if temp != "too large" and temp != "File does not exist":
					list_of_turns = temp
					loaded_map += 1
					selected_point = -1
				else:
					if loaded_map != 0:
						print("Map "+str(loaded_map+1)+" does not exist.")
						loaded_map = 0
						list_of_turns = load_from_json(loaded_map + 1)
						loaded_map += 1
						selected_point = -1
					else:
						print("Map " + str(loaded_map + 1) + " does not exist.", end=" ")
						print("No Map Are Made")
						loaded_map = 0
				if list_of_turns:
					list_of_lines = calc_lines(list_of_turns, 80)
					wall1, wall2 = colide_lines(*list_of_lines)

			if event.key == pygame.K_d:
				if loaded_map != 0:
					print("Deleting map"+str(loaded_map))
					os.remove("maps/map"+str(loaded_map)+".json")
					x = loaded_map+1
					while x>0:
						list_of_files = os.listdir("maps")
						if "map"+str(x)+".json" in list_of_files:
							os.rename("maps/map"+str(x)+".json","maps/map"+str(x-1)+".json")
							x += 1
						else:
							x = -1
					list_of_turns = []
					list_of_lines = calc_lines(list_of_turns, 80)
					wall1, wall2 = colide_lines(*list_of_lines)
					selected_point = -1
					loaded_map = 0
				else:
					print("No Map Is Selected")
				
		if event.type == pygame.MOUSEBUTTONDOWN:
			if loaded_map != 0:
				loaded_map -= 1
			if event.button == 1:
				pos = pygame.mouse.get_pos()
				if len(list_of_turns):
					if pos != list_of_turns[selected_point]:
						if selected_point == len(list_of_turns)-1:
							list_of_turns.append(pos)
						else:
							list_of_turns.insert(selected_point+1,pos)
						selected_point += 1
				else:
					list_of_turns.append(pos)
					selected_point += 1
				if len(list_of_turns) >= 2:
					list_of_lines = calc_lines(list_of_turns,80)
					wall1, wall2 = colide_lines(*list_of_lines)
			if event.button == 3:
				if len(list_of_turns):
					list_of_turns.pop(selected_point)
					selected_point -= 1
					if selected_point < 0:
						selected_point = len(list_of_turns)-1
				if len(list_of_turns) >= 2:
					list_of_lines = calc_lines(list_of_turns, 80)
					wall1, wall2 = colide_lines(*list_of_lines)
				
				
	screen.fill((0,0,0))
	draw(wall1, wall2, screen)
	if len(list_of_turns):
		for x in range(len(list_of_turns)):
			if selected_point != x:
				pygame.draw.circle(screen,(255,255,255),list_of_turns[x],5)
			else:
				pygame.draw.circle(screen,(255,0,0),list_of_turns[x],5)

	pygame.display.update()
	pygame.display.flip()

		
