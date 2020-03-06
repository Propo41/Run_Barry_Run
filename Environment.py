import heapq

import pygame

from util import TILE_SIZE, make_vector, GREEN, LIGHT_GREY, vec2int


class Walls:
    def __init__(self, x, y):  # game is the Game class object
        # self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.x = x
        self.y = y


class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.connections = [make_vector((30, 0)), make_vector((-30, 0)), make_vector((0, 30)), make_vector((0, -30))]
        # comment/uncomment this for diagonals:
        self.connections += [make_vector((30, 0)), make_vector((-30, 0)), make_vector((0, 30)), make_vector((0, -30))]

    def in_bounds(self, node):
        return 0 <= node.x < self.width and 0 <= node.y < self.height

    def passable(self, node):
        return node not in self.walls

    def find_neighbors(self, node):
        neighbors = [node + connection for connection in self.connections]
        # print("neighbors 1: ", neighbors)
        neighbors = filter(self.in_bounds, neighbors)
        neighbors = filter(self.passable, neighbors)
        return neighbors

    # draw the walls
    def draw(self, screen):
        for wall in self.walls:
            # print("size: ", wall)
            rect = pygame.Rect(wall[0], wall[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, LIGHT_GREY, rect)


class WeightedGrid(SquareGrid):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.weights = {}

    def cost(self, from_node, to_node):
        if (make_vector(to_node) - make_vector(from_node)).length_squared() == 1:
            return self.weights.get(to_node, 0) + 10
        else:
            return self.weights.get(to_node, 0) + 14

    def draw(self, screen):
        for wall in self.walls:
            rect = pygame.Rect(wall[0], wall[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, LIGHT_GREY, rect)


class PriorityQueue:
    def __init__(self):
        self.nodes = []

    def put(self, node, cost):
        heapq.heappush(self.nodes, (cost, node))

    def get(self):
        return heapq.heappop(self.nodes)[1]

    def empty(self):
        return len(self.nodes) == 0


def dijkstra_search(graph, start, end):
    frontier = PriorityQueue()
    frontier.put(vec2int(start), 0)
    path = {}
    cost = {}
    path[vec2int(start)] = None
    cost[vec2int(start)] = 0

    while not frontier.empty():
        current = frontier.get()
        if current == end:
            break
        for next in graph.find_neighbors(make_vector(current)):
            next = vec2int(next)
            next_cost = cost[current] + graph.cost(current, next)
            if next not in cost or next_cost < cost[next]:
                cost[next] = next_cost
                priority = next_cost
                frontier.put(next, priority)
                path[next] = make_vector(current) - make_vector(next)
    return path
