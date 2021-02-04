import pygame
import os
import sys
import random
import math


TANKSPEED = 5
ROTATIONSPEED = 3
BALLSPEED = 7
DISAPPEARTIME = 500
RADIUS = 5
size = width, height = 1200, 700


pygame.init()
screen = pygame.display.set_mode(size)
buttons1 = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_SPACE]


def IsCorrect(x, y):
    return 0 <= x <= width and 0 <= y <= height


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # Если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()

    return image


all_sprites = pygame.sprite.Group()


horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        if IsCorrect(x1, y1) and IsCorrect(x2, y2):
            super().__init__(all_sprites)
            if x1 == x2:  # вертикальная стенка
                self.add(vertical_borders)
                self.image = pygame.Surface([1, y2 - y1])
                self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
            else:  # горизонтальная стенка
                self.add(horizontal_borders)
                self.image = pygame.Surface([x2 - x1, 1])
                self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


Border(5, 5, width - 5, 5)
Border(5, height - 5, width - 5, height - 5)
Border(5, 5, 5, height - 5)
Border(width - 5, 5, width - 5, height - 5)


def load_level(filename):
    filename = "data/" + filename

    if not os.path.isfile(filename):
        print(f"Файл с изображением '{filename}' не найден")
        sys.exit()

    with open(filename, 'r') as mapFile:
        level_map = [list(map(int, line.strip().split())) for line in mapFile]

    return level_map


def generate_level(level):
    for i in range(len(level)):
        Border(*level[i])


generate_level(load_level("level1.txt"))


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, x, y, vx, vy):
        super().__init__(all_sprites)
        self.time = 0
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("black"),
                           (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.vx = vx
        self.vy = vy


    def update(self):
        self.time += 1
        if self.time >= DISAPPEARTIME:
            self.kill()
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx


Ball(5, 50, 50, 1, 3)


def rot_center(image, rect, angle):
    rotated_image = pygame.transform.rotate(image, angle + 90)
    new_rect = rotated_image.get_rect(center=rect.center)

    return rotated_image, new_rect


tank_group = pygame.sprite.Group()
IMAGE0 = load_image('tank_green.png', -1)


class Tank(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, Buttons, image, angle):
        super().__init__(tank_group, all_sprites)
        self.angle = angle
        self.Buttons = Buttons
        self.image = image
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def move(self, keys):
        x, y = 0, 0
        if keys[self.Buttons[0]]:
            self.angle += ROTATIONSPEED
        if keys[self.Buttons[1]]:
            self.angle -= ROTATIONSPEED
        if keys[self.Buttons[2]]:
            x = TANKSPEED * math.cos(math.radians(self.angle))
            y = - TANKSPEED * math.sin(math.radians(self.angle))
        if keys[self.Buttons[3]]:
            x = - TANKSPEED * math.cos(math.radians(self.angle))
            y = TANKSPEED * math.sin(math.radians(self.angle))

        self.angle = self.angle % 360

        if pygame.sprite.spritecollideany(self, horizontal_borders):
            if self.angle > 180:
                if y > 0:
                    y = 0
            else:
                if y < 0:
                    y = 0

        if pygame.sprite.spritecollideany(self, vertical_borders):
            if 270 > self.angle > 90:
                if x < 0:
                    x = 0
            else:
                if x > 0:
                    x = 0

        self.rect.x += round(x)
        self.rect.y += round(y)
        self.image, self.rect = rot_center(IMAGE0, self.rect, self.angle)

    def shoot(self):
        vx = BALLSPEED * math.cos(self.angle * math.pi / 180)
        vy = - BALLSPEED * math.sin(self.angle * math.pi / 180)
        Ball(RADIUS, self.rect.center[0], self.rect.center[1], vx, vy)


tank1 = Tank(500, 500, buttons1, IMAGE0, 90)


class Cursor(pygame.sprite.Sprite):
    image = load_image("arrow.png", -1)
    def __init__(self, group):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite.
        # Это очень важно !!!
        super().__init__(group)
        self.image = Cursor.image
        self.rect = self.image.get_rect()

        self.Visible = True

    def update(self, pos):
        self.rect.x, self.rect.y = pos


mouse = pygame.sprite.Group()
Cursor(mouse)

if __name__ == '__main__':
    screen.fill(pygame.Color('white'))
    time = 0

    running = True
    while running:  # главный игровой цикл
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == tank1.Buttons[4]:
                    tank1.shoot()

        keys = pygame.key.get_pressed()
        tank1.move(keys)

        screen.fill(pygame.Color('white'))

        all_sprites.draw(screen)
        all_sprites.update()

        if pygame.mouse.get_focused():
            pygame.mouse.set_visible(False)
            mouse.draw(screen)
            mouse.update(pygame.mouse.get_pos())

        pygame.time.delay(10)
        pygame.display.flip()