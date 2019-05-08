import pygame
import control
import sys
import game_objects
pygame.init()

WINDOW_SIZE_X = 1800
WINDOW_SIZE_Y = 1440

WHITE = (255, 255, 255)
BLACK = (255, 255, 255)
RED = (255, 50, 0)
NICE_BLUE = (0, 125, 255)
SKY_BLUE = (135, 206, 235)


class Button:
    def __init__(self, game_window, x, y, w, h, color, text, action=None, sender=None):
        self.text = text
        self.action = action
        self.sender = sender
        self.color = color
        self.game_window = game_window
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        pygame.draw.rect(self.game_window, self.color, self.rect)
        draw_text(self.text, self.game_window, int(self.rect.h / 2), WHITE,
                  self.rect.x + self.rect.w / 10, self.rect.y + self.rect.h / 3)

    def is_clicked(self, x, y):
        if self.rect.collidepoint(x, y):
            if self.text == "Play with Camera Control":
                self.action(control.CameraControl)
            elif self.text == "Play with Mouse Control":
                self.action(control.MouseControl)
            elif self.text == "Play again":
                self.action(self.sender.control)
            elif self.text == "Choose":
                if self.sender.text:
                    self.action(self.sender.text)
            elif self.text == "Delete player":
                self.action(self.sender.text)
                self.sender.erase()
            elif self.text == "Continue":
                return True
            else:
                self.action()
            return True


class InputBox:
    COLOR_INACTIVE = WHITE
    COLOR_ACTIVE = SKY_BLUE
    FONT_SIZE = 70
    FONT = pygame.font.Font(None, FONT_SIZE)

    def __init__(self, screen, x, y, w, h, text=''):
        self.screen = screen
        self.w = w
        self.rect = pygame.Rect(x, y, w, h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos[0], event.pos[1]):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.FONT.render(self.text, True, self.color)

    def erase(self):
        self.text = ""
        self.txt_surface = self.FONT.render(self.text, True, self.color)
        self.draw()

    def draw(self):
        width = max(self.w, self.txt_surface.get_width()+10)
        self.rect.w = width
        self.screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(self.screen, self.color, self.rect, 2)


def show_choose_player_menu(game):
    input_box = InputBox(game.game_window,
                         WINDOW_SIZE_X / 2,
                         WINDOW_SIZE_Y / 2 - 150,
                         500,
                         70)

    choose_button = Button(game.game_window,
                           WINDOW_SIZE_X / 2 - 670,
                           WINDOW_SIZE_Y / 2 + 300,
                           600, 100, NICE_BLUE,
                           "Choose",
                           game.change_user,
                           input_box)

    delete_button = Button(game.game_window,
                           WINDOW_SIZE_X / 2 + 70,
                           WINDOW_SIZE_Y / 2 + 300,
                           600, 100, NICE_BLUE,
                           "Delete player",
                           game_objects.Statistics.delete_user_from_db,
                           input_box)

    buttons = [choose_button, delete_button]

    done = False
    while not done:
        game.background.show()

        draw_text('Choose player', game.game_window, 100, WHITE,
                  (WINDOW_SIZE_X / 2 - 250), (WINDOW_SIZE_Y / 10))

        draw_text('Enter your name:', game.game_window, 70, WHITE,
                  (WINDOW_SIZE_X / 2 - 500), (WINDOW_SIZE_Y / 2 - 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            input_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.is_clicked(event.pos[0], event.pos[1])
        for button in buttons:
            button.draw()
        input_box.draw()
        pygame.display.update()


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

    def show(self, points, player):
        draw_text('Score: %s' % points, self.game_window, self.SIZE, self.COLOR, 10, 110)
        if player.get_high_score() > points:
            draw_text('Record: %s' % player.get_high_score(), self.game_window, self.SIZE, self.COLOR, 10, 150)
        else:
            draw_text('New Record!', self.game_window, self.SIZE, self.COLOR, 10, 150)


def draw_text(text, surface, font_size, color, x, y):
    text_obj = pygame.font.SysFont(None, font_size).render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


def show_main_menu(game):
    pygame.mouse.set_visible(True)

    draw_text('SPACE INVADERS', game.game_window, 200, WHITE,
              (WINDOW_SIZE_X / 2 - 600), (WINDOW_SIZE_Y / 6))

    draw_text('Hello, ' + game.username, game.game_window, 70, WHITE,
              50, 50)

    image_size = 300
    player_image_path = game_objects.Player.image_path
    image = pygame.transform.scale(pygame.image.load(player_image_path),
                                   (image_size, image_size))
    rect = pygame.Rect(WINDOW_SIZE_X / 2 - image_size / 2,
                       WINDOW_SIZE_Y / 2 - image_size / 2 - 50,
                       image_size, image_size)

    game.game_window.blit(image, rect)

    cam_button = Button(game.game_window,
                        WINDOW_SIZE_X / 2 - 670,
                        WINDOW_SIZE_Y / 2 + 250,
                        600, 100, NICE_BLUE,
                        "Play with Camera Control",
                        game.start)

    mouse_button = Button(game.game_window,
                          WINDOW_SIZE_X / 2 + 70,
                          WINDOW_SIZE_Y / 2 + 250,
                          600, 100, NICE_BLUE,
                          "Play with Mouse Control",
                          game.start)

    statistics_button = Button(game.game_window,
                               WINDOW_SIZE_X / 2 - 670,
                               WINDOW_SIZE_Y / 2 + 400,
                               600, 100, NICE_BLUE,
                               "Statistics",
                               game.statistics_menu)

    choose_player_button = Button(game.game_window,
                                  WINDOW_SIZE_X / 2 + 70,
                                  WINDOW_SIZE_Y / 2 + 400,
                                  600, 100, NICE_BLUE,
                                  "Change Player",
                                  game.choose_player_menu)

    clicks_checked(cam_button, mouse_button, statistics_button, choose_player_button)


def show_statistics_menu(game):
    stats = game.player.statistics
    pygame.mouse.set_visible(True)
    draw_text('Your Statistics', game.game_window, 150, NICE_BLUE,
              (WINDOW_SIZE_X / 3 - 100), (WINDOW_SIZE_Y / 15))
    draw_text('Records', game.game_window, 150, NICE_BLUE,
              (WINDOW_SIZE_X / 5), (WINDOW_SIZE_Y / 4))
    for i in range(stats.RECORDS_COUNT):
        draw_text(str(i + 1)+". "+str(stats.records[i]), game.game_window, 150, NICE_BLUE,
                  (WINDOW_SIZE_X / 5), (WINDOW_SIZE_Y / 4 + (i + 1) * 110))

    image_heart = pygame.transform.scale(pygame.image.load('game_pictures/heart.png'), (200, 200))
    rect_heart = pygame.Rect(WINDOW_SIZE_X / 2 + 20, WINDOW_SIZE_Y / 2 - 300, 200, 200)
    draw_text(str(stats.played_games), game.game_window, 300, NICE_BLUE,
              (WINDOW_SIZE_X / 2 + 270), (WINDOW_SIZE_Y / 2 - 290))
    game.game_window.blit(image_heart, rect_heart)

    image_ufo = pygame.transform.scale(pygame.image.load('ufo_pictures/ufo_2.png'), (200, 200))
    rect_ufo = pygame.Rect(WINDOW_SIZE_X / 2 + 20, WINDOW_SIZE_Y / 2, 200, 200)
    draw_text(str(stats.killed_enemies), game.game_window, 300, NICE_BLUE,
              (WINDOW_SIZE_X / 2 + 270), (WINDOW_SIZE_Y / 2))
    game.game_window.blit(image_ufo, rect_ufo)

    top_button = Button(game.game_window,
                        WINDOW_SIZE_X / 2 - 670,
                        WINDOW_SIZE_Y / 2 + 400,
                        600, 100, NICE_BLUE,
                        "Top Players",
                        game.top_menu)
    menu_button = Button(game.game_window,
                         WINDOW_SIZE_X / 2 + 70,
                         WINDOW_SIZE_Y / 2 + 400,
                         600, 100, NICE_BLUE,
                         "Main Menu",
                         game.main_menu)

    clicks_checked(menu_button, top_button)


def show_top_menu(game):
    records = game_objects.Statistics.get_global_records_from_db()
    pygame.mouse.set_visible(True)
    draw_text('Top Players', game.game_window, 150, NICE_BLUE,
              (WINDOW_SIZE_X / 2 - 300), (WINDOW_SIZE_Y / 15))
    for i in range(game_objects.Statistics.RECORDS_COUNT):
        draw_text(str(i + 1)+". " + records[i][1] + "  (" + str(records[i][0]) + ")", game.game_window, 150, WHITE,
                  (WINDOW_SIZE_X / 5), (WINDOW_SIZE_Y / 9 + (i + 1) * 150))

    statistics_button = Button(game.game_window,
                               WINDOW_SIZE_X / 2 - 670,
                               WINDOW_SIZE_Y / 2 + 400,
                               600, 100, NICE_BLUE,
                               "Your statistics",
                               game.statistics_menu)
    menu_button = Button(game.game_window,
                         WINDOW_SIZE_X / 2 + 70,
                         WINDOW_SIZE_Y / 2 + 400,
                         600, 100, NICE_BLUE,
                         "Main Menu",
                         game.main_menu)

    clicks_checked(menu_button, statistics_button)


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

    buttons = [continue_button, menu_button]
    cont = False
    while not cont:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                cont = continue_button.is_clicked(event.pos[0], event.pos[1])
                menu_button.is_clicked(event.pos[0], event.pos[1])
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        for b in buttons:
            b.draw()
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
        for b in buttons:
            b.draw()
        pygame.display.update()
