import pygame

SMALL = "small"
LARGE = "large"


class ExplosionAnimation:
    animation_images = {SMALL: [], LARGE: []}

    for i in range(9):
        img = pygame.image.load('explosion_animation/regularExplosion0{}.png'.format(i))
        img_large = pygame.transform.scale(img, (250, 250))
        animation_images[LARGE].append(img_large)
        img_small = pygame.transform.scale(img, (150, 150))
        animation_images[SMALL].append(img_small)

    def __init__(self, size, center, game_window):
        self.size = size
        self.game_window = game_window
        self.image = self.animation_images[size][0]
        self.rect = self.image.get_rect()
        self.center = center
        self.rect.center = center
        self.frame = 0
        self.game_window.blit(self.image, self.rect)

    def update(self):
        self.frame += 1
        if self.frame >= len(self.animation_images[self.size]):
            return False
        else:
            self.image = self.animation_images[self.size][self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = self.center
            self.game_window.blit(self.image, self.rect)
            return True
