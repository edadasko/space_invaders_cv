import interface
import pygame
import cv2.cv2 as cv2
from abc import ABC, abstractmethod


class Control(ABC):
    def __init__(self, rect):
        self.rect = rect

    @abstractmethod
    def move_object(self):
        pass


class CameraControl(Control):
    WEBCAM_SIZE_X = 600
    WEBCAM_SIZE_Y = 600
    HAAR_CASCADE_PATH = 'haar_cascades/spaceship_cascade_medium.xml'
    MIN_STEP = 5

    def __init__(self, rect):
        Control.__init__(self, rect)
        self.spaceship_cascade = cv2.CascadeClassifier(self.HAAR_CASCADE_PATH)
        self.capture = cv2.VideoCapture(0)
        self.is_object_initialized = False
        self.last_x = 0

    def move_object(self):
        ret, img = self.capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if not self.is_object_initialized:
            spaceship_detector = self.spaceship_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in spaceship_detector:
                self.is_object_initialized = True
                self.last_x = x
                self.rect.center = ((self.WEBCAM_SIZE_X - x) / self.WEBCAM_SIZE_X * interface.WINDOW_SIZE_X,
                                    interface.WINDOW_SIZE_Y * 0.8)
                return
            self.rect.center = (interface.WINDOW_SIZE_X / 2, interface.WINDOW_SIZE_Y * 0.8)
            return

        spaceship_detector = self.spaceship_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in spaceship_detector:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.imshow('Face Detection', img)
            step = (self.last_x - x) / self.WEBCAM_SIZE_X * interface.WINDOW_SIZE_X
            if abs(step) < self.MIN_STEP or \
               x / self.WEBCAM_SIZE_X * interface.WINDOW_SIZE_X < 0 or \
               x / self.WEBCAM_SIZE_X * interface.WINDOW_SIZE_X > interface.WINDOW_SIZE_X:
                return
            self.rect.move_ip(step, 0)
            self.last_x = x
            return

    def destroy(self):
        self.capture.release()
        cv2.destroyAllWindows()


class MouseControl(Control):
    def __init__(self, rect):
        Control.__init__(self, rect)
        self.is_object_initialized = False

    def move_object(self):
        if not self.is_object_initialized:
            self.rect.center = (interface.WINDOW_SIZE_X / 2, interface.WINDOW_SIZE_Y * 0.8)
            pygame.mouse.set_pos(self.rect.centerx, self.rect.centery)
            self.is_object_initialized = True
            return

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                if (event.pos[0] < 0 or event.pos[0] > interface.WINDOW_SIZE_X
                   or event.pos[1] < 0 or event.pos[1] > interface.WINDOW_SIZE_Y):
                    return
                pygame.mouse.set_pos(self.rect.centerx, self.rect.centery)
                self.rect.move_ip(event.pos[0] - self.rect.centerx, 0)

