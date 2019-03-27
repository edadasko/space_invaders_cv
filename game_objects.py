import random
import pygame
import interface


class Player:
    SIZE_X = 200
    SIZE_Y = 200
    image = pygame.transform.scale(pygame.image.load('player.png'),
                                   (SIZE_X, SIZE_Y))

    def __init__(self, current_control, game_window):
        self.game_window = game_window
        self.rect = self.image.get_rect()

        self.is_player_initialize = False
        self.last_x = 0
        self.last_y = 0
        self.control = current_control(self.rect)
        self.is_initialize = False

    def move(self):
        self.control.move_object()
        self.game_window.blit(self.image, self.rect)

    def is_collision(self, enemies):
        for en in enemies:
            if self.rect.colliderect(en.rect):
                return True
        return False

    def shoot(self):
        bullet_1 = Bullet(self.game_window, self.rect.centerx - self.SIZE_X / 4, self.rect.centery)
        bullet_2 = Bullet(self.game_window, self.rect.centerx + self.SIZE_X / 4, self.rect.centery)
        bullet_1.create()
        bullet_2.create()
        return bullet_1, bullet_2


class Bullet:
    DAMAGE = 10
    SPEED = 30
    SIZE_X = 50
    SIZE_Y = 150
    image = pygame.transform.rotate(pygame.image.load("bullet.png"), 90)

    def __init__(self, game_window, x, y):
        self.game_window = game_window
        self.x = x
        self.y = y
        self.surface = pygame.transform.scale(self.image, (self.SIZE_X, self.SIZE_Y))
        self.rect = self.surface.get_rect()
        self.rect.center = (x, y)

    def create(self):
        self.game_window.blit(self.surface, self.rect)

    def move(self):
        self.rect.move_ip(0, - self.SPEED)
        self.game_window.blit(self.surface, self.rect)

    def is_collision(self, enemies):
        for en in enemies:
            if self.rect.colliderect(en.rect):
                en.health -= self.DAMAGE
                return True
        return False


class Enemy:
    MIN_SIZE = 50
    MAX_SIZE = 150
    MIN_SPEED = 10
    MAX_SPEED = 30

    image = pygame.image.load('enemy.png')

    def __init__(self, game_window):
        self.game_window = game_window
        self.size = random.randint(self.MIN_SIZE, self.MAX_SIZE)
        self.rect = pygame.Rect(random.randint(0, interface.WINDOW_SIZE_X - self.size),
                                0 - self.size, self.size * 4, self.size)
        self.speed = random.randint(self.MIN_SPEED, self.MAX_SPEED)
        self.surface = pygame.transform.scale(self.image, (self.size * 4, self.size))
        self.health = self.size

    def create(self):
        self.game_window.blit(self.surface, self.rect)

    def move(self):
        self.rect.move_ip(0, self.speed)
        self.game_window.blit(self.surface, self.rect)
