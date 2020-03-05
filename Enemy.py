import time
from _thread import start_new_thread
from collections import deque

import pygame

from util import GREEN, vec2int, distance_from_goal, make_vector, load_images


class Enemy:
    def __init__(self, x, y, goal, g, walls):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.walls = walls
        self.color = GREEN
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.path_index = 0
        self.frontier = deque()
        self.frontier.append(make_vector((x, y)))
        self.visited = []
        self.goal = goal
        self.g = g
        self.images = load_images("Assets/Sprite/time_wraith/*.png")
        self.image_index = 0
        start_new_thread(self.enemy_movement, (None,))

    def render_enemy(self, screen, enemy_pos):
        # self.images[self.image_index].set_colorkey((255, 255, 255))
        # screen.blit(self.images[self.image_index], (enemy_pos[0], enemy_pos[1]))
        #print("enemy pos: ", enemy_pos)
        pygame.draw.rect(screen, (0, 0, 0), (enemy_pos[0], enemy_pos[1], self.width, self.height), 0)

    def get_pos(self):
        return self.rect.x, self.rect.y

    # thread
    # uses modified bfs to search the player
    # if player is caught, then the thread sleeps for 5 sec before chasing again
    # TODO: change algorithm to a multiple source shortest path or A* path finding
    # TODO: try using one which doesnt require a multi thread

    def enemy_movement(self, void):
        while len(self.frontier) > 0:
            time.sleep(0.3)
            current = self.frontier.popleft()
            # print("current, end_node =  ", current, self.goal)
            enemy_rect = pygame.Rect(current.x, current.y, self.width, self.height)
            player_rect = pygame.Rect(self.goal.x, self.goal.y, 55, 55)
            if enemy_rect.colliderect(player_rect):
                print("found!!!")
                time.sleep(3)
            # print("current: ", current)
            # path_list.append((current[0], current[1]))
            min_euclidean_distance = 10000000
            closest_neighbor = current
            stuck_counter = 0
            # print("closest: ", closest_neighbor)
            length = 0
            for neighbor in self.g.find_neighbors(current):
                # print(neighbor)
                length += 1
                if vec2int(neighbor) not in self.visited:
                    # check the distance of that neighbor against the end_node
                    self.visited.append(neighbor)
                    dist = distance_from_goal(neighbor, self.goal)
                    # ==print("dist: ", dist)
                    if dist <= min_euclidean_distance:
                        min_euclidean_distance = dist
                        closest_neighbor = neighbor
                    # if the distance is less than the previous, then min_neiighbor is that
                else:
                    # print("cant move")
                    stuck_counter += 1
            if stuck_counter >= length:
                self.visited = []
                print("stuck!")

            self.frontier.append(closest_neighbor)
            x = int(closest_neighbor[0])
            y = int(closest_neighbor[1])

            # print(closest_neighbor)
            self.rect.x = x
            self.rect.y = y

    def update_image(self):
        self.image_index += 1
        if self.image_index >= 5:
            self.image_index = 0
