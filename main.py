import pygame
import os
import sys
import random
import math
import ctypes


pygame.init()

BOARDSDENSITY = 1/2
N, M = 9, 5
TANKSPEED = 6
ROTATIONSPEED = 4
AIMINGROTATIONSPEED = 1
BALLSPEED = 6
DISAPPEARTIME = 500
RADIUS = 6
SAFETIME = 12
BORDERWIDTH = 5
BULLETS = 6
ROUNDS = 0
BOOM = []


user32 = ctypes.windll.user32
size = width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1) - 50
screen = pygame.display.set_mode(size)
buttons1 = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_SPACE, pygame.K_m]
buttons2 = [pygame.K_s, pygame.K_f, pygame.K_e, pygame.K_d, pygame.K_q, pygame.K_1]


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
                y2, y1 = max(y2, y1), min(y2, y1)
                self.image = pygame.Surface([BORDERWIDTH, y2 - y1])
                self.rect = pygame.Rect(x1, y1, BORDERWIDTH, y2 - y1)
                self.mask = pygame.mask.from_surface(self.image)
                if y2 - y1 != BORDERWIDTH - 4:
                    Border(x1 + 2, y1 + 2, x1 + BORDERWIDTH - 2, y1 + 2)
                    Border(x2 + 2, y2 - BORDERWIDTH - 2, x2 + BORDERWIDTH - 2, y2 - BORDERWIDTH - 2)
            else:  # горизонтальная стенка
                self.add(horizontal_borders)
                x2, x1 = max(x2, x1), min(x2, x1)
                self.image = pygame.Surface([x2 - x1, BORDERWIDTH])
                self.rect = pygame.Rect(x1, y1, x2 - x1, BORDERWIDTH)
                self.mask = pygame.mask.from_surface(self.image)
                if x2 - x1 != BORDERWIDTH - 4:
                    Border(x1 + 2, y1 + 2, x1 + 2, y1 + BORDERWIDTH - 2)
                    Border(x2 - BORDERWIDTH - 2, y2 + 2, x2 - BORDERWIDTH - 2, y2 + BORDERWIDTH - 2)

def make_perimetr():
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

color = []


def decision(probability):
    return random.random() < probability


def dfs(x, y):
    global color
    color[x][y][0] = 1
    m = [[-1, 0], [1, 0], [0, -1], [0, 1]]
    for i in range(len(m)):
        a = x + m[i][0]
        b = y + m[i][1]
        if 0 <= a <= N-2 and 0 <= b <= M-2:
            if color[a][b][0] == 0:
                if decision(BOARDSDENSITY):
                    color[x][y].append([a, b])
                    dfs(a, b)


def convert(x, y):
    return int(5 + (x + 1) * (width - 10) / N), int(5 + (y + 1) * (height - 10) / M)


def new_lewel():
    global color
    level = []
    color = [0] * (N-1)
    for i in range(N-1):
        color[i] = [0] * (M-1)
    for i in range(len(color)):
        for j in range(len(color[i])):
            color[i][j] = [0]

    for i in range(len(color)):
        for j in range(len(color[i])):
            if color[i][j][0] == 0:
                dfs(i, j)

    for i in range(len(color)):
        for j in range(len(color[i])):
            for x in range(1, len(color[i][j])):
                a = convert(i, j)
                b = convert(color[i][j][x][0], color[i][j][x][1])
                level.append([a[0], a[1], b[0], b[1]])
    return level


Balls = pygame.sprite.Group()


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, x, y, vx, vy, parent):
        super().__init__(all_sprites)
        self.add(Balls)
        self.time = 0
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("black"),
                           (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.mask = pygame.mask.from_surface(self.image)
        self.vx = vx
        self.vy = vy
        self.vx0 = vx
        self.vy0 = vy
        self.up_down = self.vy0 <= 0
        self.left_right = self.vx0 <= 0
        self.parent = parent


    def update(self):
        self.time += 1
        if self.time >= DISAPPEARTIME:
            if AllTanks[self.parent]:
                AllTanks[self.parent].bullets -= 1
            self.kill()

        coll1 = False
        up_down = False
        coll2 = False
        left_right = False

        for i in horizontal_borders:
            offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
            if self.mask.overlap_area(i.mask, offset) > 0:
                coll1 = True
                if self.rect.centery <= i.rect.y:
                    up_down = True
        for i in vertical_borders:
            offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
            if self.mask.overlap_area(i.mask, offset) > 0:
                coll2 = True
                if self.rect.centerx <= i.rect.x:
                    left_right = True

        if coll1:
            if up_down:
                if not self.up_down:
                    self.vy = -self.vy0
                else:
                    self.vy = self.vy0
            else:
                if self.up_down:
                    self.vy = -self.vy0
                else:
                    self.vy = self.vy0
        if coll2:
            if left_right:
                if not self.left_right:
                    self.vx = -self.vx0
                else:
                    self.vx = self.vx0
            else:
                if self.left_right:
                    self.vx = -self.vx0
                else:
                    self.vx = self.vx0

        self.rect = self.rect.move(self.vx, self.vy)


def rot_center(image, rect, angle):
    rotated_image = pygame.transform.rotate(image, angle + 90)
    new_rect = rotated_image.get_rect(center=rect.center)
    new_mask = pygame.mask.from_surface(rotated_image)

    return rotated_image, new_rect, new_mask


tank_group = pygame.sprite.Group()
AllTanks = []

for i in range(1, 6):
    BOOM.append(load_image('explosionSmoke' + str(i) + '.png', -1))

font = pygame.font.SysFont(None, 78)


class Tank(pygame.sprite.Sprite):
    def __init__(self, Buttons, image, color):
        super().__init__(tank_group, all_sprites)
        self.index = len(AllTanks)
        AllTanks.append(self)
        self.angle = random.randrange(0, 360)
        self.Buttons = Buttons
        self.image = image
        self.IMAGE0 = image
        self.bullets = 0
        self.dies = 0
        self.color = color
        self.alive = True
        self.aming = False
        x, y = random.randrange(5, width-10, width//N), random.randrange(5, height - 10, height // M)
        self.rect = self.image.get_rect().move(x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.img = font.render(str(ROUNDS - self.dies), True, self.color)

    def move(self, keys):
        x, y = 0, 0

        coll1 = False
        up_down = False
        coll2 = False
        left_right = False

        for i in horizontal_borders:
            offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
            if self.mask.overlap_area(i.mask, offset) > 0:
                coll1 = True
                if self.rect.centery < i.rect.y:
                    up_down = True
        for i in vertical_borders:
            offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
            if self.mask.overlap_area(i.mask, offset) > 0:
                coll2 = True
                if self.rect.centerx < i.rect.x:
                    left_right = True


        if keys[self.Buttons[0]]:
            if self.aming:
                self.angle += AIMINGROTATIONSPEED
            else:
                self.angle += ROTATIONSPEED

        if keys[self.Buttons[1]]:
            if self.aming:
                self.angle -= AIMINGROTATIONSPEED
            else:
                self.angle -= ROTATIONSPEED

        if keys[self.Buttons[2]]:
            x = TANKSPEED * math.cos(math.radians(self.angle))
            y = - TANKSPEED * math.sin(math.radians(self.angle))

        if keys[self.Buttons[3]]:
            x = - TANKSPEED * math.cos(math.radians(self.angle))
            y = TANKSPEED * math.sin(math.radians(self.angle))

        self.angle = self.angle % 360

        if coll1:
            if up_down:
                if y > 0:
                    y = 0
            else:
                if y < 0:
                    y = 0

        if coll2:
            if left_right:
                if x > 0:
                    x = 0
            else:
                if x < 0:
                    x = 0

        self.rect.x += round(x)
        self.rect.y += round(y)
        self.image, self.rect, self.mask = rot_center(self.IMAGE0, self.rect, self.angle)

    def shoot(self):
        if self.bullets > BULLETS:
            return
        vx = BALLSPEED * math.cos(self.angle * math.pi / 180)
        vy = - BALLSPEED * math.sin(self.angle * math.pi / 180)
        x = (self.IMAGE0.get_width()) * math.cos(self.angle * math.pi / 180) / 2
        y = - (self.IMAGE0.get_height()) * math.sin(self.angle * math.pi / 180) / 2
        self.bullets += 1
        Ball(RADIUS, self.rect.center[0] + x - RADIUS // 2, self.rect.center[1] + y - RADIUS // 2, vx, vy, self.index)

    def update(self, *args, **kwargs):
        for i in Balls:
            offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
            if self.mask.overlap_area(i.mask, offset) > 0:
                if i.time > SAFETIME or i.parent != self.index:
                    i.kill()
                    for t in BOOM:
                        self.image = t
                        screen.fill(pygame.Color('white'))
                        all_sprites.draw(screen)
                        pygame.display.flip()
                        pygame.time.delay(100)
                    pygame.time.delay(400)
                    self.alive = False
                    self.kill()
                    self.dies += 1
                    break

    def transfer(self):
        self.alive = True
        self.angle = random.randrange(0, 360)
        x, y = random.randrange(5, width - 10, width // N), random.randrange(5, height - 10, height // M)
        self.rect = self.image.get_rect().move(x, y)
        all_sprites.add(self)
        self.img = font.render(str(ROUNDS - self.dies), True, self.color)


def LivesCounter(mas):
    answer = 0
    for i in range(len(mas)):
        if mas[i].alive:
            answer += 1
    return answer


def start_screen():
    WIDTH, HEIGHT = 1280, 720

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                reunning = False
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        pygame.time.delay(10)


generate_level(new_lewel())

make_perimetr()

tank1 = Tank(buttons1, load_image('tank_green.png'), (0, 255, 0))
tank2 = Tank(buttons2, load_image('tank_red.png'), (255, 0, 0))


if __name__ == '__main__':
    screen.fill(pygame.Color('white'))
    time = 0
    start_screen()

    running = True
    while running:  # главный игровой цикл
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                for i in range(len(AllTanks)):
                    if AllTanks[i].alive:
                        if event.key == AllTanks[i].Buttons[4]:
                            AllTanks[i].shoot()
                        if event.key == AllTanks[i].Buttons[5]:
                            AllTanks[i].aming = True

            if event.type == pygame.KEYUP:
                for i in range(len(AllTanks)):
                    if AllTanks[i].alive:
                        if event.key == AllTanks[i].Buttons[5]:
                            AllTanks[i].aming = False

        keys = pygame.key.get_pressed()
        for i in range(len(AllTanks)):
            if AllTanks[i].alive:
                AllTanks[i].move(keys)

        if LivesCounter(AllTanks) < 2:
            ROUNDS += 1
            all_sprites.empty()
            vertical_borders.empty()
            horizontal_borders.empty()
            Balls.empty()
            for item in AllTanks:
                item.bullets = 0
            make_perimetr()
            generate_level(new_lewel())
            for i in range(len(AllTanks)):
                AllTanks[i].transfer()

        screen.fill(pygame.Color('white'))
        for i in range(len(AllTanks)):
            screen.blit(AllTanks[i].img, (width/2 - 30 + i * 60, 30))
        all_sprites.draw(screen)
        all_sprites.update()

        pygame.time.delay(10)
        pygame.display.flip()