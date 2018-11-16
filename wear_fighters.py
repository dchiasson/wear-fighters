import pygame
import things
import time

def update_all(thing_list):
    for thing in thing_list:
        thing.update()

def blit_all(screen, thing_list):
    for thing in sorted(thing_list, key=lambda thing: thing.blit_order):
        screen.blit(thing.get_image(), thing.position)

def main():
    pygame.init()
    pygame.display.set_caption("The best game ever...")

    screen = pygame.display.set_mode((1400,900))

    airplane = things.Airplane()
    thing_list = [airplane]

    running = True
    while running:
        # Get user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # if left button is pressed before right is release, the left turn is ignored
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    airplane.lateral_force = .02
                if event.key == pygame.K_LEFT:
                    airplane.lateral_force = -.02
                if event.key == pygame.K_UP:
                    airplane.acceleration = .1
                if event.key == pygame.K_DOWN:
                    airplane.acceleration = -.1
                if event.key == pygame.K_SPACE:
                    thing_list.append(things.Bullet(airplane))
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    airplane.lateral_force = 0
                if event.key == pygame.K_LEFT:
                    airplane.lateral_force = 0
                if event.key == pygame.K_UP:
                    airplane.acceleration = 0
                if event.key == pygame.K_DOWN:
                    airplane.acceleration = 0

        # Update object positions
        update_all(thing_list)

        # Update the display
        screen.fill((66,80,250)) # sky blue background
        blit_all(screen, thing_list)
        pygame.display.flip()
        time.sleep(.01)

if __name__ == "__main__":
    main()
