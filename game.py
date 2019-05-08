import cv2.cv2 as cv2
import pygame
import game_objects
import interface
import control
import random
import animations


class Game:
    FREQUENCY_OF_ENEMIES = 10
    FREQUENCY_OF_BULLETS = 3
    FPS = 60
    CHANGE_SCORE = 1000

    def __init__(self):
        self.username = ""
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load('sounds/background.mp3')
        self.control = control.MouseControl

        self.enemies = []
        self.bullets = []
        self.explosions = []

        self.main_clock = pygame.time.Clock()
        self.game_window = pygame.display.set_mode((interface.WINDOW_SIZE_X, interface.WINDOW_SIZE_Y))
        self.player = None
        self.background = game_objects.Background(self.game_window)

        self.health_indicator = interface.HealthIndicator(self.game_window)
        self.points_indicator = interface.PointsIndicator(self.game_window)

        self.score = 0
        self.change_score = 0
        self.difficulty = 0

        self.enemy_checker = 0
        self.bullet_checker = 0
        self.boss_bullet_checker = 0

        self.is_boss = False
        self.ufos = [game_objects.StandardUFO, game_objects.BossUFO, game_objects.SideUFO]
        self.quantity_of_level_types = 3
        self.current_level_type = 0
        self.ufo = game_objects.StandardUFO

        self.pause = False

        pygame.display.set_caption('Space Invaders')
        pygame.mouse.set_visible(True)

    def main_menu(self):
        pygame.mixer.music.stop()
        self.set_all_to_zero()
        self.background.show()
        interface.show_main_menu(self)

    def statistics_menu(self):
        self.background.show()
        interface.show_statistics_menu(self)

    def top_menu(self):
        self.background.show()
        interface.show_top_menu(self)

    def choose_player_menu(self):
        self.background.show()
        interface.show_choose_player_menu(self)

    def change_user(self, username):
        self.username = username
        self.player = game_objects.Player(self.control, self.game_window, self.username)
        self.main_menu()

    def start(self, current_control):
        self.set_all_to_zero()
        pygame.mixer.music.play(-1)
        self.control = current_control
        self.player.change_control(self.control)
        pygame.mouse.set_visible(False)

        repeat = self.update_game_window()
        while repeat:
            repeat = self.update_game_window()

        pygame.mixer.music.stop()
        interface.show_lose_menu(self)

    def update_game_window(self):
        self.background.update()
        self.score += 1
        self.change_score += 1
        self.enemy_checker += 1
        self.bullet_checker += 1
        self.boss_bullet_checker += 1
        self.player.move()

        # смена вида НЛО
        if self.change_score > self.CHANGE_SCORE and not self.is_boss:
            self.difficulty += 1
            new_level_type = self.current_level_type
            while new_level_type == self.current_level_type:
                new_level_type = random.randint(0, self.quantity_of_level_types - 1)
            self.ufo = self.ufos[new_level_type]
            self.change_score = 0
            self.current_level_type = new_level_type

        # добавление НЛО на экран
        if self.ufo is game_objects.BossUFO and not self.is_boss:
            enemy = self.ufo(self.game_window, self.difficulty)
            enemy.create()
            self.enemies.append(enemy)
            self.is_boss = True
        elif self.ufo is not game_objects.BossUFO:
            if self.enemy_checker >= self.FREQUENCY_OF_ENEMIES:
                self.enemy_checker = 0
                enemy = self.ufo(self.game_window, self.difficulty)
                enemy.create()
                self.enemies.append(enemy)

        # передвижение объектов
        for en in self.enemies:
            en.move()
        for b in self.bullets:
            b.move()

        # контроль всех НЛО (удаление, взрывы, выпуск снарядов)
        for en in self.enemies:
            if type(en) == game_objects.BossUFO and\
                    self.boss_bullet_checker > game_objects.BossUFO.FREQUENCY_OF_BULLETS and\
                    en.rect.centery >= game_objects.BossUFO.POSITION_Y:
                self.bullets.extend(en.shoot())
                self.boss_bullet_checker = 0
            if en.rect.top > interface.WINDOW_SIZE_Y or en.health < en.MIN_SIZE:
                if en.health < en.MIN_SIZE:
                    self.score += en.size
                    self.change_score += en.size
                    self.explosions.append(animations.ExplosionAnimation(animations.SMALL,
                                                                         en.rect.center,
                                                                         self.game_window))
                    if self.is_boss and type(en) == game_objects.BossUFO:
                        self.is_boss = False
                        self.score += en.size * 5
                        self.change_score = self.CHANGE_SCORE + 1
                        self.player.add_health()
                        self.explosions.append(animations.ExplosionAnimation(animations.LARGE,
                                               en.rect.center,
                                               self.game_window))
                    self.player.add_killed_enemy()
                self.enemies.remove(en)

        # удаление неактивных снарядов
        for ex in self.explosions:
            if not ex.update():
                self.explosions.remove(ex)

        # коллизии снарядов с объектами -> взрывы
        for b in self.bullets:
            if type(b) == game_objects.PlayerBullet and b.is_collision(self.enemies):
                ex = animations.ExplosionAnimation(animations.SMALL,
                                                   b.rect.center,
                                                   self.game_window)
                self.explosions.append(ex)
                self.bullets.remove(b)
                continue
            if type(b) == game_objects.BossBullet and b.is_collision(self.player):
                ex = animations.ExplosionAnimation(animations.LARGE,
                                                   self.player.rect.center,
                                                   self.game_window)
                self.explosions.append(ex)
                self.bullets.remove(b)
                continue
            if b.rect.top < 0 or b.rect.top > interface.WINDOW_SIZE_Y:
                self.bullets.remove(b)

        if self.player.is_collision(self.enemies):
            self.explosions.append(animations.ExplosionAnimation(animations.LARGE,
                                                                 self.player.rect.center,
                                                                 self.game_window))

        # проверка на смерть игрока
        if self.player.health < 1:
            self.player.add_played_game()
            self.player.update_statistics(self.score)
            return False

        # индикаторы состояния игры
        self.health_indicator.show(self.player.health)
        self.points_indicator.show(self.score, self.player)

        # нажатие мыши -> выпуск снарядов
        pressed = pygame.mouse.get_pressed()
        if self.bullet_checker > self.FREQUENCY_OF_BULLETS and \
                (pressed[0] or self.control is control.CameraControl):
            self.bullets.extend(list(self.player.shoot()))
            self.bullet_checker = 0

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    interface.show_pause_menu(self)

        if self.control is control.CameraControl:
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                return False
        self.main_clock.tick(self.FPS)
        return True

    def set_all_to_zero(self):
        self.score = 0
        self.change_score = 0
        self.enemy_checker = 0
        self.bullet_checker = 0
        self.boss_bullet_checker = 0
        self.is_boss = False
        self.ufo = game_objects.StandardUFO
        self.difficulty = 0
        self.enemies = []
        self.bullets = []
        self.explosions = []

        if self.control is control.CameraControl:
            self.player.control.destroy()


game = Game()
game.choose_player_menu()
