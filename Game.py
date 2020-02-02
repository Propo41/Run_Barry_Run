import glob
import os
import sys
import pygame

from Player import Player
from network import Network

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1020
TILE_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH / TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT / TILE_SIZE
LIGHT_GREY = (225, 225, 225)
GREEN = (0, 255, 0)
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


class Walls:
    def __init__(self, x, y):  # game is the Game class object
        # self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.x = x
        self.y = y


class Game:
    def __init__(self):
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.running = True
        self.walls = []
        self.background = pygame.image.load("Assets/background.png").convert()
        self.map_data = []
        self.player1_img = []
        self.player2_img = []
        self.init_player(1)
        self.init_player(2)
        # self.font = pygame.font.Font(None, 30)
        self.player_1 = Player(0, 0)
        self.player_2 = Player(0, 0)

        self.create_maze()
        self.game_loop()

    def game_loop(self):
        while self.running:
            self.event_handling()
            self.player_1.player_movement()
            self.display()
            # fps = self.font.render(str(int(CLOCK.get_fps())), True, pygame.Color('white'))
            # self.screen.blit(fps, (1850, 50))
            pygame.display.update()
            CLOCK.tick(FPS)

    def display(self):
        # self.screen.fill(BG_COLOUR)
        self.screen.blit(self.background, (0, 0))
        # self.draw_grid()
        for wall in self.walls:
            pygame.draw.rect(self.screen, LIGHT_GREY, wall.rect)
        self.player1_img[self.player_1.sprite_index].set_colorkey((255, 255, 255))
        self.player2_img[self.player_2.sprite_index].set_colorkey((255, 255, 255))
        # print(self.player_1.sprite_index)
        self.screen.blit(self.player1_img[self.player_1.sprite_index], self.player_1.rect)
        self.screen.blit(self.player2_img[self.player_2.sprite_index], self.player_2.rect)

        # pygame.draw.rect(self.screen, GREEN, self.player.rect)  # player
        pygame.display.update()

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            # print(x)
            pygame.draw.line(self.screen, LIGHT_GREY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, LIGHT_GREY, (0, y), (SCREEN_WIDTH, y))

    def event_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit()

    # iterates through text file given and detects game objects
    # + - | are walls
    # x, y are players
    # @ end target
    def create_maze(self):
        map_data = load_map_data(self.map_data)
        x = y = 0
        for row in map_data:
            for col in row:
                if col == "+" or col == "-" or col == "|":
                    self.walls.append(Walls(x, y))
                if col == "x":
                    # set location of player 1
                    self.player_1.set_pos(x, y)
                    # print("player 1: ", x, y)
                elif col == "y":
                    # spawn player 2
                    # print("player 2: ", x, y)
                    self.player_2.set_pos(x, y)
                    pass
                elif col == "@":
                    # spawn end target
                    pass
                x += TILE_SIZE
            y += TILE_SIZE
            x = 0
        self.player_1.set_walls(self.walls)
        self.player_2.set_walls(self.walls)

    # load images from directory
    def init_player(self, mode):
        if mode == 1:
            directory = "Assets/Sprite/flash/*.png"
        else:
            directory = "Assets/Sprite/rev_flash/*.png"
        temp_list = []
        for image in glob.glob(directory):  # extracting all file names to temp_list
            temp_list.append(image)
            temp_list.sort(key=sortKeyFunc)  # sorting templist since glob doesn't return files in order
        for image in temp_list:
            if mode == 1:
                self.player1_img.append(pygame.image.load(image).convert())
            else:
                self.player2_img.append(pygame.image.load(image).convert())


m = Game()
