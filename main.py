import pygame
import os
import sys
import random


pygame.init()
size = width, height = 500, 500
screen = pygame.display.set_mode(size)


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


class Tank:
    pass


all_sprites = pygame.sprite.Group()


horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
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


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, x, y, vx, vy):
        super().__init__(all_sprites)
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("black"),
                           (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.vx = vx
        self.vy = vy


    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx


Ball(5, 50, 50, 10, 30)


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
mouse = pygame.sprite.Group()
Cursor(mouse)


if __name__ == '__main__':
    screen.fill(pygame.Color('white'))

    running = True
    while running:  # главный игровой цикл
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.draw(screen)
        all_sprites.update()

        if pygame.mouse.get_focused():
            pygame.mouse.set_visible(False)
            mouse.draw(screen)
            mouse.update(pygame.mouse.get_pos())

        pygame.time.delay(10)
        pygame.display.flip()