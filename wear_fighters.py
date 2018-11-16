import pygame
import things
import time
import const

def update_all(thing_list):
    for thing in thing_list:
        thing.update_physics()
        if thing.position[0] < 0:
            thing.velocity[0] = -thing.velocity[0]
        if thing.position[1] < 0:
            thing.velocity[1] = -thing.velocity[1]
        if thing.position[0] > const.X_MAX:
            thing.velocity[0] = -thing.velocity[0]
        if thing.position[1] > const.Y_MAX:
            thing.velocity[1] = -thing.velocity[1]

def blit_all(screen, thing_list):
    for thing in sorted(thing_list, key=lambda thing: thing.blit_order):
        thing.blit(screen)

def main():
    pygame.init()
    pygame.display.set_caption("The best game ever...")

    screen = pygame.display.set_mode((const.X_MAX, const.Y_MAX))

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

        # Update the display
        screen.fill(const.SKY_BLUE) # sky blue background
        blit_all(screen, thing_list)
        pygame.display.flip()
        time.sleep(.01)

if __name__ == "__main__":
    main()
