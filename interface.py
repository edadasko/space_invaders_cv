import pygame
import control
import sys
import game_objects

WINDOW_SIZE_X = 1800
WINDOW_SIZE_Y = 1440

WHITE = (255, 255, 255)
BLACK = (255, 255, 255)
RED = (255, 50, 0)
NICE_BLUE = (0, 125, 255)


class Button:
    def __init__(self, game_window, x, y, w, h, color, text, action=None, sender=None):
        self.text = text
        self.action = action
        self.sender = sender
        self.game_window = game_window
        self.rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(game_window, color, self.rect)
        draw_text(text, game_window, int(h / 2), WHITE, x + w / 10, y + h / 3)

    def is_clicked(self, x, y):
        if self.rect.collidepoint(x, y):
            if self.text == "Play with Camera Control":
                self.action(control.CameraControl)
            elif self.text == "Play with Mouse Control":
                self.action(control.MouseControl)
            elif self.text == "Play again":
                self.action(self.sender.control)
            elif self.text == "Continue":
                return True
            else:
                self.action()
            return True


class HealthIndicator:
    SIZE = 100
    image = pygame.transform.scale(pygame.image.load('game_pictures/heart.png'), (SIZE, SIZE))

    def __init__(self, game_window):
        self.game_window = game_window
        self.rects = [pygame.Rect(0, 0, self.SIZE, self.SIZE),
                      pygame.Rect(self.SIZE, 0, self.SIZE, self.SIZE),
                      pygame.Rect(self.SIZE * 2, 0, self.SIZE, self.SIZE),
                      pygame.Rect(self.SIZE * 3, 0, self.SIZE, self.SIZE),
                      pygame.Rect(self.SIZE * 4, 0, self.SIZE, self.SIZE)]

    def show(self, num):
        for r in range(num):
            self.game_window.blit(self.image, self.rects[r])


class PointsIndicator:
    SIZE = 50
    COLOR = WHITE

    def __init__(self, game_window):
        self.game_window = game_window

    def show(self, points):
        draw_text('Score: %s' % points, self.game_window, self.SIZE, self.COLOR, 10, 110)


def draw_text(text, surface, font_size, color, x, y):
    text_obj = pygame.font.SysFont(None, font_size).render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


def show_main_menu(game, game_window):
    pygame.mouse.set_visible(True)

    draw_text('SPACE INVADERS', game.game_window, 200, WHITE,
              (WINDOW_SIZE_X / 2 - 610), (WINDOW_SIZE_Y / 5))

    image_size = 300
    player_image_path = game_objects.Player.image_path
    image = pygame.transform.scale(pygame.image.load(player_image_path),
                                   (image_size, image_size))
    rect = pygame.Rect(WINDOW_SIZE_X / 2 - image_size / 2,
                       WINDOW_SIZE_Y / 2 - image_size / 2 - 50,
                       image_size, image_size)

    game_window.blit(image, rect)

    cam_button = Button(game_window,
                        WINDOW_SIZE_X / 2 - 670,
                        WINDOW_SIZE_Y / 2 + 200,
                        600, 100, NICE_BLUE,
                        "Play with Camera Control",
                        game.start)
    mouse_button = Button(game_window,
                          WINDOW_SIZE_X / 2 + 70,
                          WINDOW_SIZE_Y / 2 + 200,
                          600, 100, NICE_BLUE,
                          "Play with Mouse Control",
                          game.start)

    clicks_checked(cam_button, mouse_button)


def show_lose_menu(game):
    pygame.mouse.set_visible(True)
    draw_text('GAME OVER', game.game_window, 150, RED,
              (WINDOW_SIZE_X / 2 - 300), (WINDOW_SIZE_Y / 2 - 300))
    draw_text('Your score: ' + str(game.score), game.game_window, 150, RED,
              (WINDOW_SIZE_X / 2 - 370), (WINDOW_SIZE_Y / 2 - 150))

    again_button = Button(game.game_window,
                          WINDOW_SIZE_X / 2 - 670,
                          WINDOW_SIZE_Y / 2 + 200,
                          600, 100, NICE_BLUE,
                          "Play again",
                          game.start, game)
    menu_button = Button(game.game_window,
                         WINDOW_SIZE_X / 2 + 70,
                         WINDOW_SIZE_Y / 2 + 200,
                         600, 100, NICE_BLUE,
                         "Main Menu",
                         game.main_menu)

    clicks_checked(again_button, menu_button)


def show_pause_menu(game):
    pygame.mouse.set_visible(True)
    continue_button = Button(game.game_window,
                             WINDOW_SIZE_X / 2 - 670,
                             WINDOW_SIZE_Y / 2 + 200,
                             600, 100, NICE_BLUE,
                             "Continue")
    menu_button = Button(game.game_window,
                         WINDOW_SIZE_X / 2 + 70,
                         WINDOW_SIZE_Y / 2 + 200,
                         600, 100, NICE_BLUE,
                         "Main Menu",
                         game.main_menu)

    cont = False
    while not cont:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                cont = continue_button.is_clicked(event.pos[0], event.pos[1])
                menu_button.is_clicked(event.pos[0], event.pos[1])
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()


def clicks_checked(*buttons):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in buttons:
                    b.is_clicked(event.pos[0], event.pos[1])
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
