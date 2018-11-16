import pygame
import numpy as np
import const

def rotation_matrix(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array(((c, -s), (s, c)))

class Thing(object):
    MAX_SPEED = 40
    MIN_SPEED = 0
    def __init__(self):
        self.position = np.array([500.0, 5.0])
        self.velocity = np.array([1.0, 1.0])
        self.angle = 0.0
        self.lateral_force = 0.0
        self.acceleration = 0.0
        self.blit_order = 50 # higher numbers are drawn after (or on top of) lower numbers
        self.image = None

    def get_image(self):
        return self.image

    def update_physics(self):
        # forward acceleration
        if self.acceleration:
            speed = np.linalg.norm(self.velocity)
            unit_direction = self.velocity / speed
            if (self.acceleration / speed > -1):
                self.velocity = self.velocity + self.acceleration * unit_direction

            # Limit max and min speeds
            speed = np.linalg.norm(self.velocity)
            unit_direction = self.velocity / speed
            if speed < self.MIN_SPEED:
                self.velocity = unit_direction * self.MIN_SPEED
            elif speed > self.MAX_SPEED:
                self.velocity = unit_direction * self.MAX_SPEED

        # lateral acceleration
        if self.lateral_force:
            self.velocity = rotation_matrix(self.lateral_force).dot(self.velocity)

        # update position
        self.position += self.velocity

    def blit(self, screen):
        screen.blit(self.get_image(), self.position)


class Airplane(Thing):
    MIN_SPEED = .3
    MAX_SPEED = 20
    def __init__(self):
        super(Airplane, self).__init__()
        self.image = pygame.image.load("resources/airplane_40.png")

    def update_physics(self):
        super(Airplane, self).update_physics()
        # Always point the airplane nose in the direction of travel
        self.angle = np.arctan(self.velocity[0] / self.velocity[1]) * 180.0 / np.pi + 90
        if self.velocity[1] < 0:
            self.angle += 180

    def get_image(self):
        return pygame.transform.rotate(self.image, self.angle)


class Bullet(Thing):
    BULLET_SPEED = 6
    def __init__(self, owner):
        super(Bullet, self).__init__()
        self.velocity = owner.velocity * (1 + self.BULLET_SPEED / np.linalg.norm(owner.velocity))
        self.position = owner.position * 1.0 # arrays are mutable, so make a copy
        self.owner = owner
        
    def blit(self, screen):
        pygame.draw.rect(screen, ((0,0,0)), (self.position, [5,5]))

class Cloud(Thing):
    CLOUD_SPEED = .5
    def __init__(self):
        super(Cloud, self).__init__()
        self.image = pygame.image.load("resources/cloud_90.png")
        self.position = np.array([np.random.rand() * const.X_MAX, np.random.rand() * const.Y_MAX])
        self.velocity = rotation_matrix(np.random.rand() * 2 * np.pi).dot(np.array([0, self.CLOUD_SPEED]))
