import time
from _thread import start_new_thread

import pygame

from Graph import dijkstra_search
from util import vec2int, make_vector, load_images, TILE_SIZE


# TODO: add more enemies on triggers

class Enemy:
    def __init__(self, pos, goal, g, walls):
        # initialization
        self.x = pos[0]
        self.y = pos[1]
        self.width = 30
        self.height = 30
        self.walls = walls
        self.g = g

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # variables for dijkstra's algorithm
        self.goal = goal
        self.update_pos = False

        self.start = pos
        self.path = []

        # image sprite stuff
        self.images = load_images("Assets/Sprite/time_wraith/*.png")
        self.image_index = 0

        self.chase_player()

    def chase_player(self):
        start_new_thread(self.enemy_movement, (None,))

    def render_enemy(self, screen, enemy_pos):
        # self.images[self.image_index].set_colorkey((255, 255, 255))
        # self.images[self.image_index].set_colorkey((0, 0, 0))
        # screen.blit(self.images[self.image_index], (enemy_pos[0], enemy_pos[1]))
        pygame.draw.rect(screen, (38, 38, 38), (enemy_pos[0], enemy_pos[1], self.width, self.height), 0)

    def get_pos(self):
        return self.rect.x, self.rect.y

    # thread
    # uses dijktra's algorithm to search the player
    # if player is caught, then the thread sleeps for 1 sec before chasing again
    # TODO: try using one which doesnt require a multi thread
    def enemy_movement(self, void):
        while True:
            self.start = (make_vector((self.rect.x, self.rect.y)) // TILE_SIZE) * 30
            self.path = dijkstra_search(self.g, (self.goal // TILE_SIZE) * 30, self.start)

            try:
                current = self.start + self.path[vec2int(self.start)]
            except TypeError:  # if enemy reaches player, then an exception occurs.
                print("MOVE!")
                time.sleep(1)
                continue
            # print("path: ", self.path[vec2int(self.start)])
            while current != self.goal:
                if self.update_pos:
                    self.update_pos = False
                    break
                # print("current: ", current, " self.goal: ", self.goal)
                time.sleep(0.3)
                self.rect.x = current.x
                self.rect.y = current.y
                # find next in path
                try:
                    current = current + self.path[vec2int(current)]
                except TypeError:  # if enemy reaches player, then an exception occurs.
                    print("caught you suckaa!!")
                    time.sleep(0.5)
                    break

    def update_image(self):
        self.image_index += 1
        if self.image_index >= 5:
            self.image_index = 0

    def update_player_pos(self, player_current_pos):
        self.update_pos = True
        self.goal = (player_current_pos // TILE_SIZE) * 30
