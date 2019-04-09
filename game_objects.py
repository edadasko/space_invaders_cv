import random
import pygame
import interface
from abc import ABC, abstractmethod
pygame.mixer.init()


class Player:
    SIZE_X = 200
    SIZE_Y = 200
    MAX_HEALTH = 5
    health = 3

    image = pygame.transform.scale(pygame.image.load('player.png'),
                                   (SIZE_X, SIZE_Y))

    def __init__(self, current_control, game_window):
        self.shoot_sound = pygame.mixer.Sound("sounds/player_shoot.wav")
        self.shoot_sound.set_volume(0.5)
        self.collision_sound = pygame.mixer.Sound("sounds/explosion_1.wav")
        self.collision_sound.set_volume(0.5)
        self.game_window = game_window
        self.rect = self.image.get_rect()
        self.control = current_control(self.rect)

    def move(self):
        self.control.move_object()
        self.game_window.blit(self.image, self.rect)

    def is_collision(self, enemies):
        for en in enemies:
            if self.rect.colliderect(en.rect):
                self.collision_sound.play()
                self.health -= 1
                enemies.remove(en)
                return True
        return False

    def shoot(self):
        self.shoot_sound.play()
        bullet_1 = Bullet(self.game_window, self.rect.centerx - self.SIZE_X / 4, self.rect.centery, self)
        bullet_2 = Bullet(self.game_window, self.rect.centerx + self.SIZE_X / 4, self.rect.centery, self)
        bullet_1.create()
        bullet_2.create()
        return bullet_1, bullet_2

    def add_health(self):
        if self.health < self.MAX_HEALTH:
            self.health += 1


class Bullet:
    DAMAGE = 15
    SPEED = 30
    SIZE_X = 50
    SIZE_Y = 150
    collision_sounds = [pygame.mixer.Sound("sounds/explosion_1.wav"),
                        pygame.mixer.Sound("sounds/explosion_2.wav")]
    for s in collision_sounds:
        s.set_volume(0.5)
    image = pygame.transform.rotate(pygame.image.load("bullet.png"), 90)

    boss_images = [pygame.transform.rotate(pygame.image.load("boss_bullet.png"), 0),
                   pygame.transform.rotate(pygame.image.load("boss_bullet.png"), -45),
                   pygame.transform.rotate(pygame.image.load("boss_bullet.png"), 45)]

    quantity_of_types = 3

    def __init__(self, game_window, x, y, owner):
        self.owner = owner
        self.game_window = game_window
        self.x = x
        self.y = y
        if type(self.owner) == Player:
            self.surface = pygame.transform.scale(self.image, (self.SIZE_X, self.SIZE_Y))
        elif type(self.owner) == BossUFO:
            self.type = random.randint(0, self.quantity_of_types - 1)
            self.surface = pygame.transform.scale(self.boss_images[self.type], (self.SIZE_X * 2, self.SIZE_Y * 2))
        self.rect = pygame.Rect(x, y, self.SIZE_X * 0.8, self.SIZE_Y * 0.8)
        self.rect.center = (x, y)

    def create(self):
        self.game_window.blit(self.surface, self.rect)

    def move(self):
        if type(self.owner) == Player:
            self.rect.move_ip(0, - self.SPEED)
            self.game_window.blit(self.surface, self.rect)
        elif type(self.owner) == BossUFO:
            if self.type == 0:
                self.rect.move_ip(0, self.SPEED)
            elif self.type == 1:
                self.rect.move_ip(-self.SPEED, self.SPEED)
            elif self.type == 2:
                self.rect.move_ip(self.SPEED, self.SPEED)
            self.game_window.blit(self.surface, self.rect)

    def is_collision(self, enemies, player):
        if type(self.owner) == Player:
            for en in enemies:
                if self.rect.colliderect(en.rect):
                    self.collision_sounds[1].play()
                    if type(en) == BossUFO:
                        en.health -= int(self.DAMAGE / 5)
                    elif type(en) == BackUFO:
                        en.health -= int(self.DAMAGE / 2)
                    else:
                        en.health -= self.DAMAGE
                    return True
            return False

        elif type(self.owner) == BossUFO:
            if self.rect.colliderect(player.rect):
                self.collision_sounds[0].play()
                player.health -= 1
                return True
            return False


class UFO(ABC):
    MIN_SIZE = 200
    MAX_SIZE = 500
    MIN_SPEED = 10
    MAX_SPEED = 30

    image = None
    surface = None

    def __init__(self, game_window):
        self.game_window = game_window
        self.size = random.randint(self.MIN_SIZE, self.MAX_SIZE)
        self.rect = pygame.Rect(random.randint(0, interface.WINDOW_SIZE_X - self.size),
                                0 - self.size, self.size, self.size * 0.8)
        self.speed = random.randint(self.MIN_SPEED, self.MAX_SPEED)
        self.health = self.size

    def create(self):
        self.game_window.blit(self.surface, self.rect)

    @abstractmethod
    def move(self):
        pass


class StandardUFO(UFO):
    images = [pygame.image.load('ufo_pictures/ufo_2.png'),
              pygame.image.load('ufo_pictures/ufo_3.png')]
    count_of_images = 2

    def __init__(self, game_window):
        UFO.__init__(self, game_window)
        self.image = self.images[random.randint(0, self.count_of_images - 1)]
        self.surface = pygame.transform.scale(self.image, (self.size, self.size))

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.health > 0:
            self.surface = pygame.transform.scale(self.image, (self.health, self.health))
            center = self.rect.centerx, self.rect.centery
            self.rect.size = self.health, self.health * 0.8
            self.rect.center = center
        self.game_window.blit(self.surface, self.rect)


class BackUFO(UFO):
    MIN_SIZE = 150
    MAX_SIZE = 250
    MAX_SPEED = 20

    images = [pygame.image.load('ufo_pictures/back_ufo.png'),
              pygame.transform.flip(pygame.image.load('ufo_pictures/back_ufo.png'), True, False)]

    def __init__(self, game_window):
        UFO.__init__(self, game_window)
        self.type = random.randint(0, 1)
        if self.type == 0:
            self.rect = pygame.Rect(interface.WINDOW_SIZE_X + self.size,
                                    random.randint(- interface.WINDOW_SIZE_Y / 3, interface.WINDOW_SIZE_Y / 5),
                                    self.size * 2, self.size)

        else:
            self.rect = pygame.Rect(- self.size * 2,
                                    random.randint(- interface.WINDOW_SIZE_Y / 3, interface.WINDOW_SIZE_Y / 5),
                                    self.size * 2, self.size)

        self.image = self.images[self.type]
        self.surface = pygame.transform.scale(self.image, (self.size * 2, self.size))

    def move(self):
        if self.type == 0:
            self.rect.move_ip(-self.speed * 2, self.speed)
        else:
            self.rect.move_ip(self.speed * 2, self.speed)
        if self.health > 0:
            self.surface = pygame.transform.scale(self.image, (self.health * 2, self.health))
            center = self.rect.centerx, self.rect.centery
            self.rect.size = self.health * 2, self.health
            self.rect.center = center
        self.game_window.blit(self.surface, self.rect)


class BossUFO(UFO):
    MIN_SIZE = 300
    FREQUENCY_OF_BULLETS = 6
    POSITION_Y = interface.WINDOW_SIZE_Y / 7
    images = [pygame.image.load('ufo_pictures/boss_1.png'),
              pygame.image.load('ufo_pictures/boss_2.png')]
    count_of_images = 2

    shoot_sound = pygame.mixer.Sound("sounds/player_shoot.wav")
    shoot_sound.set_volume(0.5)

    def __init__(self, game_window):
        UFO.__init__(self, game_window)
        pygame.mixer.init()
        self.size = 800
        self.health = self.size
        self.speed = 10
        self.image = self.images[random.randint(0, self.count_of_images - 1)]
        self.surface = pygame.transform.scale(self.image, (self.size * 2, self.size))
        self.rect = pygame.Rect(interface.WINDOW_SIZE_X / 2 - self.size, 0 - self.size, self.size * 2, self.size * 0.6)

    def move(self):
        if self.rect.centery < self.POSITION_Y:
            self.rect.move_ip(0, self.speed)
        if self.health > 0:
            self.surface = pygame.transform.scale(self.image, (self.health * 2, self.health))
            center = self.rect.centerx, self.rect.centery
            self.rect.size = self.health * 2, self.health * 0.6
            self.rect.center = center
        self.game_window.blit(self.surface, self.rect)

    def shoot(self):
        self.shoot_sound.play()
        bullet = Bullet(self.game_window,
                        random.randint(self.rect.centerx - int(self.size / 3), self.rect.centerx + int(self.size / 3)),
                        self.rect.centery + 100, self)
        bullet.create()
        return bullet


class Background:
    speed = 10
    image = pygame.transform.scale(pygame.image.load("space.png"),
                                   (interface.WINDOW_SIZE_X, interface.WINDOW_SIZE_Y))

    def __init__(self, game_window):
        self.rects = [self.image.get_rect(), self.image.get_rect()]
        self.rects[0].center = interface.WINDOW_SIZE_X / 2, interface.WINDOW_SIZE_Y / 2
        self.rects[1].center = interface.WINDOW_SIZE_X / 2, - interface.WINDOW_SIZE_Y / 2
        self.game_window = game_window

    def show(self):
        self.game_window.blit(self.image, self.rects[0])
        self.game_window.blit(self.image, self.rects[1])

    def update(self):
        for r in self.rects:
            if r.centery > interface.WINDOW_SIZE_Y / 2 * 3:
                self.rects.remove(r)
                new_rect = self.image.get_rect()
                new_rect.center = interface.WINDOW_SIZE_X / 2, - interface.WINDOW_SIZE_Y / 2
                self.rects.append(new_rect)
            r.move_ip(0, self.speed)
            self.game_window.blit(self.image, r)

