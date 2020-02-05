import os

import pygame

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1020
TILE_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH / TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT / TILE_SIZE

LIGHT_GREY = (225, 225, 225)
GREEN = (0, 255, 0)
YELLOW = (0, 150, 150)
BG_COLOUR = (255, 255, 255)

CLOCK = pygame.time.Clock()
FPS = 60


# empty list map_data is sent
def load_map_data(map_data):
    try:
        with open("Assets/map_data.txt", "rt") as f:
            for line in f:
                map_data.append(line)
            return map_data
    except pygame.error as e:
        print("file not found")


def sortKeyFunc(s):
    return int(os.path.basename(s)[:-4])


def get_spawn_location():
    map_data = []
    map_data = load_map_data(map_data)
    x1 = y1 = 0
    x2 = y2 = 0
    x = y = 0
    for row in map_data:
        for col in row:
            if col == "x":
                # set location of player 1
                x1 = x
                y1 = y
            elif col == "y":
                # spawn player 2
                x2 = x
                y2 = y
            elif col == "@":
                # spawn end target
                pass
            x += TILE_SIZE
        y += TILE_SIZE
        x = 0
    return [(x1, y1), (x2, y2)]
