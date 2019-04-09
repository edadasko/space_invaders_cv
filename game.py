import cv2.cv2 as cv2
import sys
import pygame
import game_objects
import interface
import control
import random


class Game:
    FREQUENCY_OF_ENEMIES = 10
    FREQUENCY_OF_BULLETS = 3
    FPS = 60
    CHANGE_SCORE = 1000

    def __init__(self):
        pygame.mixer.music.load('sounds/background.mp3')
        pygame.init()
        self.control = control.MouseControl
        self.enemies = []
        self.bullets = []
        self.main_clock = pygame.time.Clock()
        self.game_window = pygame.display.set_mode((interface.WINDOW_SIZE_X, interface.WINDOW_SIZE_Y))
        self.player = game_objects.Player(self.control, self.game_window)
        self.background = game_objects.Background(self.game_window)
        self.health_indicator = interface.HealthIndicator(self.game_window)
        self.points_indicator = interface.PointsIndicator(self.game_window)

        pygame.display.set_caption('lab_2')
        pygame.mouse.set_visible(True)

    def show_menu(self):
        self.background.show()
        b_1 = interface.Button(self.game_window,
                               interface.WINDOW_SIZE_X / 3,
                               interface.WINDOW_SIZE_Y / 2 - 300,
                               600, 100, (0, 125, 255),
                               "Camera Control",
                               self.start)
        b_2 = interface.Button(self.game_window,
                               interface.WINDOW_SIZE_X / 3,
                               interface.WINDOW_SIZE_Y / 2 - 100,
                               600, 100, (0, 125, 255),
                               "Mouse Control",
                               self.start)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    b_1.is_clicked(event.pos[0], event.pos[1])
                    b_2.is_clicked(event.pos[0], event.pos[1])
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    def start(self, current_control):
        pygame.mixer.music.play()
        self.control = current_control
        self.enemies.clear()
        self.bullets.clear()
        self.player = game_objects.Player(self.control, self.game_window)
        pygame.mouse.set_visible(False)
        score = 0
        change_score = 0
        is_active = True
        enemy_checker = 0
        bullet_checker = 0
        boss_bullet_checker = 0
        is_boss = False
        ufos = [game_objects.StandardUFO, game_objects.BossUFO, game_objects.BackUFO]
        quantity_of_level_types = 3
        current_level_type = 0
        ufo = game_objects.StandardUFO
        while is_active:
            self.background.update()
            score += 1
            change_score += 1
            enemy_checker += 1
            bullet_checker += 1
            boss_bullet_checker += 1
            self.player.move()

            if change_score > self.CHANGE_SCORE and not is_boss:
                new_level_type = current_level_type
                while new_level_type == current_level_type:
                    new_level_type = random.randint(0, quantity_of_level_types - 1)
                ufo = ufos[new_level_type]
                change_score = 0
                current_level_type = new_level_type

            if ufo is game_objects.BossUFO and not is_boss:
                enemy = ufo(self.game_window)
                enemy.create()
                self.enemies.append(enemy)
                is_boss = True
            elif ufo is not game_objects.BossUFO:
                if enemy_checker >= self.FREQUENCY_OF_ENEMIES:
                    enemy_checker = 0
                    enemy = ufo(self.game_window)
                    enemy.create()
                    self.enemies.append(enemy)

            for en in self.enemies:
                if type(en) == game_objects.BossUFO and\
                        boss_bullet_checker > game_objects.BossUFO.FREQUENCY_OF_BULLETS and\
                        en.rect.centery >= game_objects.BossUFO.POSITION_Y:
                    self.bullets.append(en.shoot())
                    boss_bullet_checker = 0
                if en.rect.top > interface.WINDOW_SIZE_Y or en.health < en.MIN_SIZE:
                    if en.health < en.MIN_SIZE:
                        score += en.size
                        change_score += en.size
                        if is_boss and type(en) == game_objects.BossUFO:
                            is_boss = False
                            score += en.size * 5
                            change_score = self.CHANGE_SCORE + 1
                            self.player.add_health()
                    self.enemies.remove(en)

            for b in self.bullets:
                if b.rect.top < 0 or b.rect.top > interface.WINDOW_SIZE_Y \
                        or b.is_collision(self.enemies, self.player):
                    self.bullets.remove(b)

            for en in self.enemies:
                en.move()

            for b in self.bullets:
                b.move()

            self.player.is_collision(self.enemies)

            if self.player.health < 1:
                break

            self.health_indicator.show(self.player.health)
            self.points_indicator.show(score)

            pygame.display.update()

            pressed = pygame.mouse.get_pressed()
            if bullet_checker > self.FREQUENCY_OF_BULLETS and \
                    (pressed[0] or self.control is control.CameraControl):
                self.bullets.extend(list(self.player.shoot()))
                bullet_checker = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_active = False

            if self.control is control.CameraControl:
                k = cv2.waitKey(30) & 0xff
                if k == 27:
                    break
            self.main_clock.tick(self.FPS)

        pygame.mixer.music.stop()
        interface.draw_text('GAME OVER', self.game_window, 100, (255, 255, 255),
                            (interface.WINDOW_SIZE_X / 2), (interface.WINDOW_SIZE_Y / 2))
        interface.draw_text('Your score: ' + str(score), self.game_window, 100, (255, 255, 255),
                            (interface.WINDOW_SIZE_X / 2), (interface.WINDOW_SIZE_Y / 2 + 100))
        interface.draw_text('Press a key to play again.', self.game_window, 100, (255, 255, 255),
                            (interface.WINDOW_SIZE_X / 2), (interface.WINDOW_SIZE_Y / 2) + 200)
        pygame.display.update()
        self.restart()

    def restart(self):
        if self.control is control.CameraControl:
            self.player.control.destroy()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mouse.set_visible(True)
                        self.show_menu()
                    self.start(self.control)


game = Game()
game.show_menu()
