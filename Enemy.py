from collections import deque

import pygame

from util import GREEN


def vec2int(v):
    return int(v.x), int(v.y)


def make_vector(point):
    vec = pygame.Vector2()
    vec.xy = point[0], point[1]
    return vec


def breadth_first_search(graph, start_node, end_node):
    frontier = deque()
    frontier.append(start_node)
    path = {vec2int(start_node): None}
    path_list = []
    while len(frontier) > 0:
        current = frontier.popleft()
        # print("current: ", current)
        path_list.append((current[0], current[1]))
        for neighbor in graph.find_neighbors(current):
            if vec2int(neighbor) not in path:
                frontier.append(neighbor)
                path[vec2int(neighbor)] = current - neighbor
    return path_list


class Enemy:
    def __init__(self, x, y, path):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.color = GREEN
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.path_index = 0
        self.path = path

    def render_enemy(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)

    def update(self):
        self.rect.x = int(self.path[self.path_index][0])
        self.rect.y = int(self.path[self.path_index][1])
        self.path_index += 1
