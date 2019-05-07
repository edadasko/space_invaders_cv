import random
import pygame
import interface
from pymongo import MongoClient
from abc import ABC, abstractmethod
pygame.mixer.init()


class Player:
    SIZE_X = 200
    SIZE_Y = 200
    MAX_HEALTH = 5
    health = 3

    image_path = 'game_pictures/player.png'
    image = pygame.transform.scale(pygame.image.load(image_path),
                                   (SIZE_X, SIZE_Y))

    def __init__(self, current_control, game_window, player_name):
        self.statistics = Statistics(player_name)
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
        bullet_1 = PlayerBullet(self.game_window, self.rect.centerx - self.SIZE_X / 4, self.rect.centery, self)
        bullet_2 = PlayerBullet(self.game_window, self.rect.centerx + self.SIZE_X / 4, self.rect.centery, self)
        bullet_1.create()
        bullet_2.create()
        return bullet_1, bullet_2

    def add_health(self):
        if self.health < self.MAX_HEALTH:
            self.health += 1

    def update_statistics(self, score):
        for i in range(self.statistics.RECORDS_COUNT):
            if score > self.statistics.records[i]:
                self.statistics.records[i+1:self.statistics.RECORDS_COUNT] \
                    = self.statistics.records[i:self.statistics.RECORDS_COUNT - 1]
                self.statistics.records[i] = score
                break
        self.statistics.save_user_to_db()

    def add_killed_enemy(self):
        self.statistics.killed_enemies += 1

    def add_played_game(self):
        self.statistics.played_games += 1

    def get_high_score(self):
        return self.statistics.records[0]

    def change_control(self, control):
        self.health = 3
        self.control = control(self.rect)

    def delete_statistics(self):
        self.statistics.delete_user_from_db()


class Bullet(ABC):
    DAMAGE = 15
    SPEED = 30
    SIZE_X = 50
    SIZE_Y = 150

    surface = rect = None

    def __init__(self, game_window, x, y, owner):
        self.owner = owner
        self.game_window = game_window
        self.x = x
        self.y = y

    def create(self):
        self.game_window.blit(self.surface, self.rect)

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def is_collision(self, objects):
        pass


class PlayerBullet(Bullet):
    image = pygame.transform.rotate(pygame.image.load("bullets_pictures/bullet.png"), 90)
    collision_sound = pygame.mixer.Sound("sounds/explosion_2.wav")
    collision_sound.set_volume(0.5)

    def __init__(self, game_window, x, y, owner):
        Bullet.__init__(self, game_window, x, y, owner)
        self.surface = pygame.transform.scale(self.image, (self.SIZE_X, self.SIZE_Y))
        self.rect = pygame.Rect(x, y, self.SIZE_X * 0.8, self.SIZE_Y * 0.8)
        self.rect.center = (x, y)

    def move(self):
        self.rect.move_ip(0, - self.SPEED)
        self.game_window.blit(self.surface, self.rect)

    def is_collision(self, objects):
        for en in objects:
            if type(en) != Player and self.rect.colliderect(en.rect):
                self.collision_sound.play()
                if type(en) == BossUFO:
                    en.health -= int(self.DAMAGE / 5)
                elif type(en) == SideUFO:
                    en.health -= int(self.DAMAGE / 2)
                else:
                    en.health -= self.DAMAGE
                return True
        return False


class BossBullet(Bullet):
    images = [pygame.transform.rotate(pygame.image.load("bullets_pictures/boss_bullet.png"), 0),
              pygame.transform.rotate(pygame.image.load("bullets_pictures/boss_bullet.png"), -45),
              pygame.transform.rotate(pygame.image.load("bullets_pictures/boss_bullet.png"), 45)]
    quantity_of_types = 3

    collision_sound = pygame.mixer.Sound("sounds/explosion_1.wav")
    collision_sound.set_volume(0.5)

    def __init__(self, game_window, x, y, owner):
        Bullet.__init__(self, game_window, x, y, owner)
        self.type = random.randint(0, self.quantity_of_types - 1)
        self.surface = pygame.transform.scale(self.images[self.type], (self.SIZE_X * 2, self.SIZE_Y * 2))
        self.rect = pygame.Rect(x, y, self.SIZE_X * 0.8, self.SIZE_Y * 0.8)
        self.rect.center = (x, y)

    def move(self):
        if self.type == 0:
            self.rect.move_ip(0, self.SPEED)
        elif self.type == 1:
            self.rect.move_ip(-self.SPEED, self.SPEED)
        elif self.type == 2:
            self.rect.move_ip(self.SPEED, self.SPEED)
        self.game_window.blit(self.surface, self.rect)

    def is_collision(self, player):
        if type(player) == Player and self.rect.colliderect(player.rect):
            self.collision_sound.play()
            player.health -= 1
            return True
        return False


class UFO(ABC):
    MIN_SIZE = 200
    MAX_SIZE = 500
    min_speed = 10
    max_speed = 30

    image = None
    surface = None

    def __init__(self, game_window, difficulty):
        self.game_window = game_window
        self.size = random.randint(self.MIN_SIZE, self.MAX_SIZE)
        self.rect = pygame.Rect(random.randint(0, interface.WINDOW_SIZE_X - self.size),
                                0 - self.size, self.size, self.size * 0.8)
        self.speed = random.randint(self.min_speed, self.max_speed)
        self.speed += difficulty
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

    def __init__(self, game_window, difficulty):
        UFO.__init__(self, game_window, difficulty)
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


class SideUFO(UFO):
    MIN_SIZE = 100
    MAX_SIZE = 250
    max_speed = 20

    images = [pygame.image.load('ufo_pictures/back_ufo.png'),
              pygame.transform.flip(pygame.image.load('ufo_pictures/back_ufo.png'), True, False)]

    def __init__(self, game_window, difficulty):
        UFO.__init__(self, game_window, difficulty)
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

    def __init__(self, game_window, difficulty):
        UFO.__init__(self, game_window, difficulty)
        pygame.mixer.init()
        self.difficulty = difficulty
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
        bullets = []
        for i in range(int(self.difficulty / 5) + 1):
            bullet = BossBullet(self.game_window,
                                random.randint(self.rect.centerx - int(self.size / 3),
                                               self.rect.centerx + int(self.size / 3)),
                                self.rect.centery + 100, self)
            bullet.create()
            bullets.append(bullet)
        return bullets


class Background:
    speed = 10
    image = pygame.transform.scale(pygame.image.load("game_pictures/space.png"),
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


class Statistics:
    RECORDS_COUNT = 5
    records = []
    for i in range(RECORDS_COUNT):
        records.append(0)
    killed_enemies = 0
    played_games = 0

    def __init__(self, username):
        self.username = username
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.space_invaders.users
        self.upload_user_from_db()

    def upload_user_from_db(self):
        data = self.db.find_one({"username": self.username})
        if data:
            self.records = data["records"]
            self.killed_enemies = data["killed_enemies"]
            self.played_games = data["played_games"]
        else:
            self.reset_data()
            self.save_user_to_db()

    def save_user_to_db(self):
        self.db.update({'username': self.username},
                       {'username': self.username, 'records': self.records,
                        'killed_enemies': self.killed_enemies, 'played_games': self.played_games},
                       upsert=True)

    def reset_data(self):
        self.records = []
        for i in range(self.RECORDS_COUNT):
            self.records.append(0)
        self.killed_enemies = 0
        self.played_games = 0

    @staticmethod
    def delete_user_from_db(username):
        client = MongoClient('localhost', 27017)
        db = client.space_invaders.users
        db.remove({'username': username}, True)
