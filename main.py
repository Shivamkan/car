import pygame
import sys

pygame.init()

screen_size = (800, 600)
screen = pygame.display.set_mode(screen_size, vsync=True)

max_speed = 5


def handle_events():
    keys = {'left': False, 'right': False, 'up': False, 'down': False}
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
    return keys


class car:
    def __init__(self, x, y, stearing, angle):
        self.pos = pygame.Vector2(x, y)
        self.size = pygame.Vector2(100, 50)
        self.angle = angle
        self.dir = pygame.Vector2(1, 0).rotate(self.angle)
        self.stearing = stearing
        self.speed = pygame.Vector2(0, 0)
        self.carbody = pygame.image.load('carbody.png')
        self.carbody = pygame.transform.scale(self.carbody, self.size)

    def draw(self, screen):
        tempsurf = pygame.transform.rotate(self.carbody, self.angle)
        screen.blit(tempsurf, self.pos - pygame.Vector2(tempsurf.get_rect().size) / 2)

    def update(self, keys):
        self.speed = pygame.Vector2()
        if keys['up']:
            self.speed = pygame.Vector2(1, 0).rotate(self.angle) * max_speed
        if keys['down']:
            self.speed = pygame.Vector2(1, 0).rotate(self.angle) * -max_speed

        current_steering = 0
        if keys['left']:
            current_steering -= self.stearing
        if keys['right']:
            current_steering += self.stearing
        front_wheel, back_wheel = self.calcwheel()
        # print(front_wheel)
        back_wheel = back_wheel + self.speed
        print(current_steering)
        temp = pygame.Vector2(front_wheel)
        front_wheel += pygame.Vector2(self.dir).rotate(current_steering).normalize() * self.speed.length()
        print(front_wheel - temp if front_wheel - temp != 0 else "", end="")
        dir = front_wheel - back_wheel
        if keys['up']:
            self.speed = dir.normalize() * max_speed
        if keys['down']:
            self.speed = dir.normalize() * -max_speed
        self.dir = dir.normalize()
        self.pos = (front_wheel + back_wheel) / 2
        self.angle = -dir.as_polar()[1]

        pygame.draw.circle(screen, (255, 0, 0), self.pos, 5)
        pygame.draw.circle(screen, (0, 255, 0), front_wheel, 5)
        pygame.draw.circle(screen, (0, 0, 255), back_wheel, 5)

    def rotateAnim(self):
        self.angle += 1
        pygame.draw.circle(screen, (255, 0, 0), self.pos, 5)

    def calcwheel(self):
        dir = self.dir
        front_wheel = self.pos + dir * self.size.x * 0.4
        back_wheel = self.pos - dir * self.size.x * 0.4
        return front_wheel, back_wheel


car = car(500, 300, 15, 180)
clock = pygame.time.Clock()

while True:
    clock.tick(60)
    screen.fill((100, 100, 100))
    keys = handle_events()
    # print(keys)
    car.draw(screen)
    car.update(keys)
    pygame.display.flip()
