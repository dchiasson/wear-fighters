import pygame
import numpy as np

def rotation_matrix(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array(((c, -s), (s, c)))

class Thing(object):
    def __init__(self):
        self.position = np.array([500.0, 5.0])
        self.speed = np.array([1.0, 1.0])
        self.angle = 0.0
        self.lateral_force = 0.0
        self.acceleration = 0.0
        self.blit_order = 50 # higher numbers are drawn after (or on top of) lower numbers
        self.image = None

    def get_image(self):
        return self.image

    def update(self):
        if self.acceleration:
            self.speed *= self.acceleration
        if self.lateral_force:
            self.speed = rotation_matrix(self.lateral_force).dot(self.speed)
        self.position += self.speed

class Airplane(Thing):
    def __init__(self):
        super(Airplane, self).__init__()
        self.image = pygame.image.load("resources/airplane_40.png")

    def update(self):
        super(Airplane, self).update()
        self.angle = np.arctan(self.speed[0] / self.speed[1]) * 180.0 / np.pi + 90
        if self.speed[1] < 0:
            self.angle += 180

    def get_image(self):
        return pygame.transform.rotate(self.image, self.angle)

class Bullet(Thing):
    BULLET_SPEED = 2
    def __init__(self, owner):
        super(Bullet, self).__init__()
        self.image = pygame.image.load("resources/airplane_40.png")
        self.speed = owner.speed * (1 + self.BULLET_SPEED / np.linalg.norm(owner.speed))
        self.position = owner.position * 1.0 # arrays are mutable, so make a copy
