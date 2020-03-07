import math
import time
from _thread import start_new_thread

import pygame

from Graph import dijkstra_search
from util import vec2int, make_vector, load_images, TILE_SIZE


# TODO: add more enemies on triggers

def euclidean_distance(start, goal):
    distance = math.sqrt(pow(goal[1] - start[1], 2) + pow(goal[0] - start[0], 2))
    print("Euclidean distance from x to y: ", distance)
    return distance
    pass


class Enemy:
    def __init__(self, pos, goal, g, walls):
        # initialization
        self.x = pos[0]
        self.y = pos[1]
        self.width = 30
        self.height = 30
        self.walls = walls
        self.g = g
        self.neg_speed = 0.5  # higher the value, lower the speed

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
            while current != self.goal:
                if self.update_pos:
                    self.update_pos = False
                    break
                # print("current: ", current, " self.goal: ", self.goal)
                time.sleep(self.neg_speed)
                self.rect.x = current.x
                self.rect.y = current.y
                self.change_speed()
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

    def change_speed(self):
        if euclidean_distance(self.start, self.goal) > 150:
            self.neg_speed = 0.2  # if distance between enemy and player is high, then increase speed
        else:
            self.neg_speed = 0.4  # else reduce speed
