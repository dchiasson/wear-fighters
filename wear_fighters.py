import pygame
import things
import time
import const
import sensor_data
import threading
import queue

iteration = 0

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
        if thing.state == things.DEAD:
            thing_list.remove(thing)

def blit_all(screen, thing_list):
    for thing in sorted(thing_list, key=lambda thing: thing.blit_order):
        thing.blit(screen)

def update_ai(enemy_list, thing_list):
    global iteration
    if iteration %50 == 10:
        for enemy in enemy_list:
            if enemy.state == things.ALIVE:
                thing_list.append(things.Bullet(enemy))

end_string = "Game Over"
def check_game_end(player_list, enemy_list):
    for enemy in enemy_list:
        if enemy.state == things.ALIVE:
            return False
    if sum([player.state == things.ALIVE for player in player_list]) == 1:
        for player_index, player in enumerate(player_list):
            if player.state == things.ALIVE:
                global end_string
                end_string = "Player {} wins!".format(player_index)
                return True

def main():
    pygame.init()
    pygame.display.set_caption("The best game ever...")

    data_queue = queue.Queue()
    t = threading.Thread(target=sensor_data.sensor_listener, args=(data_queue,))
    t.daemon = True
    t.start()

    screen = pygame.display.set_mode((const.X_MAX, const.Y_MAX))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("comicsansms", 50)
    text = font.render("Waiting for sensor data...", True, (128, 128, 0))

    screen.fill(const.SKY_BLUE) # sky blue background
    screen.blit(text, ((const.X_MAX - text.get_width()) // 2, (const.Y_MAX - text.get_width()) // 2))
    pygame.display.flip()
    
    global iteration

    do_restart = True
    while do_restart:

        thing_list = []
        enemy_list = []
        player_list = []

        for _ in range(0):
            enemy = things.EnemyShip()
            thing_list.append(enemy)
            enemy_list.append(enemy)
        for cloud in range(5):
            thing_list.append(things.Cloud())



        running = True
        while running:
            iteration += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    do_restart = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_q, pygame.K_END, pygame.K_DELETE, pygame.K_ESCAPE]:
                        running = False
                        do_restart = False
                    elif event.key in [pygame.K_SPACE, pygame.K_r]:
                        running = False

            data_point = data_queue.get()

            for player_index, data_point in enumerate(data_queue.get()):
                if player_index >= len(player_list):
                    new_player = things.PlayerAirplane(player_index)
                    player_list.append(new_player)
                    thing_list.append(new_player)
                player = player_list[player_index]
                if not player.state == things.ALIVE:
                    continue

                player.set_angle(data_point.Y * 4.0)
                if data_point.R > -10:
                    if iteration % 10 == 0:
                        thing_list.append(things.Bullet(player))

            update_ai(enemy_list, thing_list)

            # Update object positions
            update_all(thing_list)
            check_collisions(thing_list)

            # Update the display
            screen.fill(const.SKY_BLUE) # sky blue background
            blit_all(screen, thing_list)
            pygame.display.flip()
            clock.tick(const.FRAME_RATE)
            #clock.get_time())

            if check_game_end(player_list, enemy_list):
                running = False
                do_restart = False

    global end_string
    text = font.render(end_string, True, (128, 128, 0))

    screen.fill(const.SKY_BLUE) # sky blue background
    screen.blit(text, ((const.X_MAX - text.get_width()) // 2, (const.Y_MAX - text.get_width()) // 2))
    pygame.display.flip()

if __name__ == "__main__":
    main()
