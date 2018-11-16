import pygame
import things
import time
import const

def update_all(thing_list):
    for thing in thing_list:
        thing.update_physics()

def check_collisions(thing_list):
    # Check for collisions of each thing with each other thing
    for thing in thing_list:
        thing.check_walls()
        for other_thing in thing_list:
            if thing is not other_thing:
                if (thing.mask.overlap(other_thing.mask,
                        (other_thing.position - thing.position).astype(int))):
                    thing.collide_with(other_thing)
    # Remove dead things from our update list
    for thing in thing_list:
        if not thing.is_alive:
            thing_list.remove(thing)

def blit_all(screen, thing_list):
    for thing in sorted(thing_list, key=lambda thing: thing.blit_order):
        thing.blit(screen)

def main():
    pygame.init()
    pygame.display.set_caption("The best game ever...")

    screen = pygame.display.set_mode((const.X_MAX, const.Y_MAX))
    clock = pygame.time.Clock()

    airplane = things.Airplane()
    thing_list = [airplane]
    for cloud in range(5):
        thing_list.append(things.Cloud())

    running = True
    while running:
        # Get user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    airplane.lateral_force += const.PLANE_TURN_RATE
                if event.key == pygame.K_LEFT:
                    airplane.lateral_force += -const.PLANE_TURN_RATE
                if event.key == pygame.K_UP:
                    airplane.acceleration += const.PLANE_ACCELERATION
                if event.key == pygame.K_DOWN:
                    airplane.acceleration += -const.PLANE_ACCELERATION
                if event.key == pygame.K_SPACE:
                    thing_list.append(things.Bullet(airplane))
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    airplane.lateral_force -= const.PLANE_TURN_RATE
                if event.key == pygame.K_LEFT:
                    airplane.lateral_force -= -const.PLANE_TURN_RATE
                if event.key == pygame.K_UP:
                    airplane.acceleration -= const.PLANE_ACCELERATION
                if event.key == pygame.K_DOWN:
                    airplane.acceleration -= -const.PLANE_ACCELERATION

        # Update object positions
        update_all(thing_list)
        check_collisions(thing_list)

        # Update the display
        screen.fill(const.SKY_BLUE) # sky blue background
        blit_all(screen, thing_list)
        pygame.display.flip()
        clock.tick(50)
        #clock.get_time())

if __name__ == "__main__":
    main()
