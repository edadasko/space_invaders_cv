import cv2.cv2 as cv2
import sys
import pygame
import game_objects
import interface
import control


class Game:
    FREQUENCY_OF_ENEMIES = 10
    FREQUENCY_OF_BULLETS = 3
    FPS = 60

    def __init__(self):
        pygame.init()
        self.control = control.MouseControl
        self.enemies = []
        self.bullets = []
        self.main_clock = pygame.time.Clock()
        self.game_window = pygame.display.set_mode((interface.WINDOW_SIZE_X, interface.WINDOW_SIZE_Y))
        self.player = game_objects.Player(self.control, self.game_window)
        self.background = game_objects.Background(self.game_window)

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
        self.control = current_control
        self.enemies.clear()
        self.bullets.clear()
        self.player = game_objects.Player(self.control, self.game_window)
        pygame.mouse.set_visible(False)
        score = 0
        is_active = True
        enemy_checker = 0
        bullet_checker = 0
        while is_active:
            self.background.update()
            score += 1
            enemy_checker += 1
            bullet_checker += 1

            self.player.move()

            if enemy_checker == self.FREQUENCY_OF_ENEMIES:
                enemy_checker = 0
                enemy = game_objects.UFO(self.game_window)
                enemy.create()
                self.enemies.append(enemy)

            for en in self.enemies:
                if en.rect.top > interface.WINDOW_SIZE_Y or en.health < 1:
                    score += en.size
                    self.enemies.remove(en)

            for b in self.bullets:
                if b.rect.top < 0 or b.is_collision(self.enemies):
                    self.bullets.remove(b)

            for en in self.enemies:
                en.move()

            for b in self.bullets:
                b.move()

            if self.player.is_collision(self.enemies):
                break

            interface.draw_text('Score: %s' % score, self.game_window, 50, (255, 255, 255), 10, 0)
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
