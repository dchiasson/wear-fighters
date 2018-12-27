import pygame
import numpy as np
import const

[ALIVE, EXPLODING, DEAD] = range(3)

def rotation_matrix(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array(((c, -s), (s, c)))

class HealthBar(object):
    HIGHT = 60
    WIDTH = 10
    def __init__(self, x, y):
        self.position = np.array([x, y])

    def blit(self, screen, health):
        pygame.draw.rect(screen, (const.WHITE), (self.position, [self.WIDTH, self.HIGHT]))
        pygame.draw.rect(screen, (const.RED), (self.position, [self.WIDTH, self.HIGHT*health]))

class Thing(object):
    MAX_SPEED = 40
    MIN_SPEED = 0
    def __init__(self, surface):
        self.image = surface
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.position = np.array([500.0, 5.0])
        self.velocity = np.array([1.0, 1.0])
        self.angle = 0
        self.scale = 1
        self.lateral_force = 0.0
        self.acceleration = 0.0
        self.blit_order = 50 # higher numbers are drawn after (or on top of) lower numbers
        self.state = ALIVE
        self.is_solid = True

    def __str__(self):
        return "{} object at position {}, velocity {}".format(type(self), self.position, self.velocity)

    def get_image(self):
        return self.image

    def update_physics(self):
        # forward acceleration
        if self.acceleration:
            speed = max(np.linalg.norm(self.velocity), 1e-8)
            unit_direction = self.velocity / speed
            if (self.acceleration / speed > -1):
                self.velocity = self.velocity + self.acceleration * unit_direction

            # Limit max and min speeds
            speed = max(np.linalg.norm(self.velocity), 1e-8)
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

    def set_angle(self, degree):
        rad = np.deg2rad(degree)
        speed = max(np.linalg.norm(self.velocity), 1e-8)
        self.velocity = speed * np.array([np.cos(rad), np.sin(rad)])
        
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

    def collide_with(self, other_object):
        if other_object.is_solid:
            self.state = DEAD


class Airplane(Thing):
    MIN_SPEED = .3
    MAX_SPEED = 20
    IMAGE_FRONT_ANGLE = 90
    EXPLOSION_LEN = const.FRAME_RATE * 2 # two seconds
    def __init__(self, image_addr=None):
        if image_addr:
            super(Airplane, self).__init__(
                    pygame.image.load(image_addr))
        else:
            super(Airplane, self).__init__(
                    pygame.image.load("resources/airplane_40.png"))


    def update_physics(self):
        super(Airplane, self).update_physics()

    def get_image(self):
        if self.state == EXPLODING:
            self.explosion_time += 1
            if (self.explosion_time > self.EXPLOSION_LEN):
                self.state = DEAD
            if (self.explosion_time % (const.FRAME_RATE // 8) == 1):
                self.angle = np.random.rand() * 360
                self.scale = 2.0 * (1.0 - float(self.explosion_time) / self.EXPLOSION_LEN)
            return pygame.transform.rotozoom(self.image, self.angle, self.scale)

        # Always point the airplane nose in the direction of travel
        if (self.velocity[1] == 0):
            self.velocity[1] = 1e-8
        self.angle = np.arctan(self.velocity[0] / self.velocity[1]) * 180.0 / np.pi + self.IMAGE_FRONT_ANGLE
        if self.velocity[1] < 0:
            self.angle += 180
        return pygame.transform.rotate(self.image, self.angle)

    def trigger_explosion(self):
        self.state = EXPLODING
        self.is_solid = False
        self.image = pygame.image.load("resources/explode_50.png")
        self.velocity = np.array([0,0])
        self.explosion_time = 0

    def collide_with(self, other_object):
        if self.state in [EXPLODING, DEAD]:
            return
        if other_object.is_solid:
            self.trigger_explosion()

class PlayerAirplane(Airplane):
    HEALTH_MAX = 5
    def __init__(self, player_index):
        super(PlayerAirplane, self).__init__("resources/airplane_40.png")
        self.health = self.HEALTH_MAX
        self.player_index = player_index
        self.health_bar = HealthBar(30+ 20 * player_index,30)
        self.velocity = 10

    def collide_with(self, other_object):
        if self.state in [EXPLODING, DEAD]:
            return
        if other_object.is_solid:
            self.health -= 1
            if self.health <= 0:
                self.trigger_explosion()
                
    def check_walls(self):
        """Just keep the players on the screen"""
        if self.position[0] < 0:
            self.position[0] = 5
        if self.position[1] < 0:
            self.position[1] = 5
        if self.position[0] > const.X_MAX:
            self.position[0] = const.X_MAX - 5
        if self.position[1] > const.Y_MAX:
            self.position[1] = const.Y_MAX - 5

    def blit(self, screen):
        super(PlayerAirplane, self).blit(screen)
        self.health_bar.blit(screen, float(self.health) / self.HEALTH_MAX)

class EnemyShip(Airplane):
    IMAGE_FRONT_ANGLE = 180
    MAX_SPEED = 5
    def __init__(self):
        super(EnemyShip, self).__init__("resources/boss_40.png")
        self.position = np.array([np.random.rand() * const.X_MAX, np.random.rand() * const.Y_MAX])
        self.velocity = rotation_matrix(np.random.rand() * 2 * np.pi).dot(np.array([0, np.random.rand()*self.MAX_SPEED]))
        self.health = 0

    def collide_with(self, other_object):
        if self.state in [EXPLODING, DEAD]:
            return
        if other_object.is_solid:
            if isinstance(other_object, EnemyShip):
                return
            if isinstance(other_object, Bullet):
                if isinstance(other_object.owner, EnemyShip):
                    return
            self.health -= 1
            if self.health <= 0:
                self.trigger_explosion()


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
        
    def blit(self, screen):
        pygame.draw.rect(screen, (const.RED), (self.position, [6,6]))

    def check_walls(self):
        """Default wall collision behavior is to bounce"""
        if self.position[0] < 0 or self.position[1] < 0 or \
                self.position[0] > const.X_MAX or self.position[1] > const.Y_MAX:
            self.state = DEAD

    def collide_with(self, other_object):
        self.state = DEAD # even clouds can destroy bullets


class Cloud(Thing):
    CLOUD_SPEED = .5
    def __init__(self):
        super(Cloud, self).__init__(
                pygame.image.load("resources/cloud_90.png"))
        self.position = np.array([np.random.rand() * const.X_MAX, np.random.rand() * const.Y_MAX])
        self.velocity = rotation_matrix(np.random.rand() * 2 * np.pi).dot(np.array([0, self.CLOUD_SPEED]))
        self.blit_order = 90
        self.is_solid = False

    def collide_with(self, other_object):
        return # I'm a cloud, I don't care
