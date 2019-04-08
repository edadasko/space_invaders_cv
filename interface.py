import pygame
import control

WINDOW_SIZE_X = 1800
WINDOW_SIZE_Y = 1440


class Button:
    def __init__(self, game_window, x, y, w, h, color, text, action):
        self.text = text
        self.action = action
        self.game_window = game_window
        self.rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(game_window, color, self.rect)
        draw_text(text, game_window, int(h / 2), (255, 255, 255), x + w / 10, y + h / 3)

    def is_clicked(self, x, y):
        if self.rect.collidepoint(x, y):
            if self.text == "Camera Control":
                self.action(control.CameraControl)
            elif self.text == "Mouse Control":
                    self.action(control.MouseControl)
            return True


class HealthIndicator:
    SIZE = 100
    image = pygame.transform.scale(pygame.image.load('heart.png'), (SIZE, SIZE))

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
    COLOR = (255, 255, 255)

    def __init__(self, game_window):
        self.game_window = game_window

    def show(self, points):
        draw_text('Score: %s' % points, self.game_window, self.SIZE, (255, 255, 255), 10, 110)


def draw_text(text, surface, font_size, color, x, y):
    text_obj = pygame.font.SysFont(None, font_size).render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

