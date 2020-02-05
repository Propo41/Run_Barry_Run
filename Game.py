import glob
import os
import sys
import pygame

from Enemy import breadth_first_search, vec2int, Enemy
from network import Network
from util import load_map_data, sortKeyFunc, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, CLOCK, FPS, LIGHT_GREY, GREEN

INTERVAL = pygame.USEREVENT + 1
pygame.time.set_timer(INTERVAL, 200)


class Walls:
    def __init__(self, x, y):  # game is the Game class object
        # self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.x = x
        self.y = y


def make_vector(point):
    vec = pygame.Vector2()
    vec.xy = point[0], point[1]
    return vec


class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.connections = [make_vector((30, 0)), make_vector((-30, 0)), make_vector((0, 30)), make_vector((0, -30))]

    def in_bounds(self, node):
        return 0 <= node.x < self.width and 0 <= node.y < self.height

    def passable(self, node):
        return node not in self.walls

    def find_neighbors(self, node):
        neighbors = [node + connection for connection in self.connections]
        # print("neighbors 1: ", neighbors)
        if (node.x + node.y) % 2:
            neighbors.reverse()
        neighbors = filter(self.in_bounds, neighbors)
        # for neighbor in neighbors:
        #     if neighbor in self.walls:
        #         print("colliding wall: ", neighbor.x, neighbor.y)
        # a quicker faster way is written in the method passable()
        neighbors = filter(self.passable, neighbors)
        # print("neighbors final: ", list(neighbors))
        return neighbors

    def draw(self, screen):
        for wall in self.walls:
            # print("size: ", wall)
            rect = pygame.Rect(wall[0], wall[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GREEN, rect)


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
        self.n = Network()
        self.player_1 = self.n.fetch_initial_data()
        self.walls_coordinate_vector = []  # holds the vector2 object of all wall coordinates
        self.create_map()
        print("walls: ", self.walls_coordinate_vector)
        self.g = SquareGrid(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.g.walls = self.walls_coordinate_vector
        self.start = make_vector((30, 30))  # a valid pos must be given that resembles a real top-left corner of a grid
        self.goal = make_vector((768, 500))  # a valid pos must be given that resembles a real top-left corner of a grid
        self.path = breadth_first_search(self.g, self.start, self.goal)
        print(self.path)
        self.enemy = Enemy(30, 30, self.path)
        # self.g.find_neighbors(make_vector((30, 30)))
        self.game_loop()

    def game_loop(self):
        while self.running:
            CLOCK.tick(FPS)
            self.fetch_data_server()
            self.event_handling()
            self.player_1.player_movement(self.walls)
            self.display()
            pygame.display.update()

    def display(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_grid()
        for wall in self.walls:
            pygame.draw.rect(self.screen, LIGHT_GREY, wall.rect)

        if self.player_1.mode == 1:
            self.player_1.render(self.screen, self.player1_img[self.player_1.sprite_index])
            self.player_2.render(self.screen, self.player2_img[self.player_2.sprite_index])
        else:
            self.player_1.render(self.screen, self.player2_img[self.player_1.sprite_index])
            self.player_2.render(self.screen, self.player1_img[self.player_2.sprite_index])
        # self.g.draw(self.screen)
        #print(self.mpos)
        self.enemy.render_enemy(self.screen)
        pygame.display.update()

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            # print(x)
            pygame.draw.line(self.screen, LIGHT_GREY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, LIGHT_GREY, (0, y), (SCREEN_WIDTH, y))

    def event_handling(self):
        self.mpos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit()
            if event.type == INTERVAL:
                # move enemy
                self.enemy.update()
                pass

            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     mpos = make_vector(pygame.mouse.get_pos())
            #     if event.button == 1:
            #         if mpos in self.g.walls:
            #             self.g.walls.remove(mpos)
            #         else:
            #             self.g.walls.append(mpos)

    # iterates through text file given and detects game objects
    # + - | are walls
    # x, y are players
    # @ end target
    def create_map(self):
        map_data = load_map_data(self.map_data)
        x = y = 0
        for row in map_data:
            for col in row:
                if col == "+" or col == "-" or col == "|":
                    self.walls.append(Walls(x, y))
                    vec = pygame.Vector2()
                    vec.xy = x, y
                    self.walls_coordinate_vector.append(vec)  # adds all coordinates of wall objects in map
                elif col == "@":
                    # spawn barry's mom
                    pass
                x += TILE_SIZE
            y += TILE_SIZE
            x = 0
        # print(list(walls_coordinate_vector))

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

    def fetch_data_server(self):
        self.player_2 = self.n.send_and_receive(self.player_1)


m = Game()
