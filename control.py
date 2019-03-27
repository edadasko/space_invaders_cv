import cv2
import interface
import pygame


class CameraControl:
    WEBCAM_SIZE_X = 400
    WEBCAM_SIZE_Y = 400
    HAAR_CASCADE_PATH = '/home/edadasko/haarcascades/haarcascade_frontalface_default.xml'
    MIN_STEP = 5

    def __init__(self, rect):
        self.face_cascade = cv2.CascadeClassifier(self.HAAR_CASCADE_PATH)
        self.capture = cv2.VideoCapture(0)
        self.is_object_initialized = False
        self.is_face_detected = False
        self.rect = rect
        self.last_x = 0
        self.last_y = 0

    def move_object(self):
        ret, img = self.capture.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if not self.is_object_initialized:
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
                cv2.imshow('img', img)
                self.rect.center = (interface.WINDOW_SIZE_X - x / self.WEBCAM_SIZE_X * interface.WINDOW_SIZE_X,
                                    interface.WINDOW_SIZE_Y * 0.8)
                self.is_object_initialized = True
                self.last_x = x
                self.last_y = y
                return
            self.rect.center = (interface.WINDOW_SIZE_X / 2, interface.WINDOW_SIZE_Y * 0.8)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.imshow('img', img)
            step = (self.last_x - x) / self.WEBCAM_SIZE_X * interface.WINDOW_SIZE_X
            if abs(step) < self.MIN_STEP or \
               x / self.WEBCAM_SIZE_X * interface.WINDOW_SIZE_X < 0 or \
               x / self.WEBCAM_SIZE_X * interface.WINDOW_SIZE_X > interface.WINDOW_SIZE_X:
                self.rect.move_ip((0, 0))
                return
            self.rect.move_ip(step, 0)
            self.is_face_detected = True
            self.last_x = x
            self.last_y = y
            return

        if not self.is_face_detected:
            self.rect.move_ip((0, 0))
            self.is_face_detected = False
            return

    def destroy(self):
        self.capture.release()
        cv2.destroyAllWindows()


class MouseControl:
    def __init__(self, rect):
        self.rect = rect
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
