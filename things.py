import pygame
import numpy as np
import const

def rotation_matrix(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array(((c, -s), (s, c)))

class Thing(object):
    MAX_SPEED = 40
    MIN_SPEED = 0
    def __init__(self, surface):
        self.image = surface
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.position = np.array([500.0, 5.0])
        self.velocity = np.array([1.0, 1.0])
        self.angle = 0.0
        self.lateral_force = 0.0
        self.acceleration = 0.0
        self.blit_order = 50 # higher numbers are drawn after (or on top of) lower numbers
        self.is_alive = True
        self.is_solid = True

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

    def check_walls(self):
        """Default wall collision behavior is to bounce"""
        if self.position[0] < 0:
            self.velocity[0] = -self.velocity[0]
        if self.position[1] < 0:
            self.velocity[1] = -self.velocity[1]
        if self.position[0] > const.X_MAX:
            self.velocity[0] = -self.velocity[0]
        if self.position[1] > const.Y_MAX:
            self.velocity[1] = -self.velocity[1]

    def check_collision(self, other_object):
        if self is other_object or not other_object.is_solid:
            return
        if (self.mask.overlap(other_object.mask,
                (other_object.position - self.position).astype(int))):
            self.is_alive = False


class Airplane(Thing):
    MIN_SPEED = .3
    MAX_SPEED = 20
    def __init__(self):
        super(Airplane, self).__init__(
                pygame.image.load("resources/airplane_40.png"))


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
        bullet_surface = pygame.Surface((6,6), pygame.SRCALPHA)
        pygame.draw.rect(bullet_surface, const.RED, ((0,0),(6,6)))
        super(Bullet, self).__init__(bullet_surface)
        owner_direction = owner.velocity / np.linalg.norm(owner.velocity)
        self.velocity = owner.velocity + owner_direction * self.BULLET_SPEED
        self.position = owner.position + max(owner.rect) * owner_direction
        self.owner = owner
        print(max(owner.rect))
        
    def blit(self, screen):
        pygame.draw.rect(screen, (const.RED), (self.position, [6,6]))


class Cloud(Thing):
    CLOUD_SPEED = .5
    def __init__(self):
        super(Cloud, self).__init__(
                pygame.image.load("resources/cloud_90.png"))
        self.position = np.array([np.random.rand() * const.X_MAX, np.random.rand() * const.Y_MAX])
        self.velocity = rotation_matrix(np.random.rand() * 2 * np.pi).dot(np.array([0, self.CLOUD_SPEED]))
        self.blit_order = 90
        self.is_solid = False

    def check_collision(self, other_object):
        return # I'm a cloud, I don't care
