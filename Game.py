import os
import sys

import pygame

from Enemy import Enemy
from util import load_map_data, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, CLOCK, FPS, LIGHT_GREY, GREEN, \
    make_vector, spawn_enemy, load_images

# TODO: add game over music
# TODO: add code to play in multiple maps

CHARACTER_SPRITEINTERVAL = pygame.USEREVENT + 1
pygame.time.set_timer(CHARACTER_SPRITEINTERVAL, 600)

CHARACTER_MOVE = pygame.USEREVENT + 2
pygame.time.set_timer(CHARACTER_MOVE, 200)

VICTORY_WINDOW = pygame.USEREVENT + 3
pygame.time.set_timer(VICTORY_WINDOW, 1000)


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

    def draw(self, screen):
        for wall in self.walls:
            # print("size: ", wall)
            rect = pygame.Rect(wall[0], wall[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GREEN, rect)


class Game:
    def __init__(self, n, p1, p2):

        # pygame initialization
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # game initialization
        self.n = n
        self.player_1 = p1
        self.player_2 = p2
        self.running = True
        self.game_over = False

        # temporary variables to counter bugs
        # TODO: fix the bug
        self.target_trigger_temp = False  # used for a random bug, in create_map(), the coordinate is fetched twice

        # image loading stuff
        self.background = pygame.image.load("Assets/background/background.png").convert()
        self.player1_img = load_images("Assets/Sprite/flash/*.png")
        self.player2_img = load_images("Assets/Sprite/rev_flash/*.png")
        self.target_img_front = [pygame.image.load("Assets/Sprite/barry_mom/front1.png").convert(),
                                 pygame.image.load("Assets/Sprite/barry_mom/front3.png").convert()]
        self.target_img_back = [pygame.image.load("Assets/Sprite/barry_mom/back1.png").convert(),
                                pygame.image.load("Assets/Sprite/barry_mom/back2.png").convert()]
        self.end_game_images = [pygame.image.load("Assets/background/p1_wins.png").convert(),
                                pygame.image.load("Assets/background/p2_wins.png").convert()]

        # map and wall stuff
        self.walls = []
        self.map_data = []
        self.walls_coordinate_vector = []  # holds the vector2 object of all wall coordinates
        self.g = SquareGrid(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.g.walls = self.walls_coordinate_vector
        self.create_map()

        # barry's mom.
        # TODO: optimize code using an array
        self.target_img_back_index = 0
        self.target_img_front_index = 0
        self.target_up = False
        self.target_down = True
        self.target_upper_limit = self.target_pos.y
        self.target_lower_limit = self.target_pos.y + (30 * 2)  # barry's mom will walk upto 3 cells downwards

        # enemy stuff
        enemy_pos = spawn_enemy(self.map_data)
        # spawns enemy and it immediately starts to follow player on a different thread
        self.enemy_1 = Enemy(enemy_pos[0], enemy_pos[1],
                             make_vector((self.player_1.rect.x, self.player_1.rect.y)), self.g, self.walls)

        # music stuff
        pygame.mixer.music.load('Assets/music/flash_theme.wav')
        pygame.mixer.music.play(-1)

        self.game_loop()

    def game_loop(self):
        while self.running:
            CLOCK.tick(FPS)
            self.fetch_data_server()
            self.event_handling()
            self.check_collision()
            self.character_mechanics()
            self.display()
            pygame.display.update()

    # checks collision between player and enemy or barry's mom.
    def check_collision(self):
        if self.player_1.rect.colliderect(self.target_pos):  # if player 1 collides with barry's mom game over
            # player 1 victory
            self.player_1.victory = True
            self.game_over = True
            self.player_1.game_over = True
            self.player_2.game_over = True
        if self.player_1.rect.colliderect(self.enemy_1.rect):  # if player 1 collides with wraith, he slows down
            # slow down player's velocity if hit by enemy
            self.player_1.velocity = 1
        else:
            self.player_1.velocity = 2

    def display(self):
        if not self.game_over:
            self.render_world()
            self.render_characters()
        else:  # IF GAME OVER
            if self.player_1.mode == 1 and self.player_1.victory:
                # if player 1 wins
                self.screen.blit(self.end_game_images[0], (0, 0))
            else:
                # if player 2 wins
                self.screen.blit(self.end_game_images[1], (0, 0))

        pygame.display.update()

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            # print(x)
            pygame.draw.line(self.screen, LIGHT_GREY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, LIGHT_GREY, (0, y), (SCREEN_WIDTH, y))

    def event_handling(self):
        self.mpos = pygame.mouse.get_pos()
        print(self.mpos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit()
            if event.type == CHARACTER_SPRITEINTERVAL:
                # change sprite index: barry's mom
                if self.target_down:
                    self.target_img_front_index += 1
                    if self.target_img_front_index > 1:
                        self.target_img_front_index = 0

                elif self.target_up:
                    self.target_img_back_index += 1
                    if self.target_img_back_index > 1:
                        self.target_img_back_index = 0
            if event.type == CHARACTER_MOVE:
                vel = 1
                if self.target_up:
                    self.target_pos.y -= vel
                    if self.target_pos.y <= self.target_upper_limit:
                        self.target_down = True
                        self.target_up = False
                if self.target_down:
                    self.target_pos.y += vel
                    if self.target_pos.y >= self.target_lower_limit:
                        self.target_down = False
                        self.target_up = True
            if event.type == VICTORY_WINDOW and (self.player_1.game_over or self.player_2.game_over):
                sys.exit(0)

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
                elif col == "@" and not self.target_trigger_temp:
                    # print("mom: ", x, y)
                    self.target_trigger_temp = True
                    self.target_pos = pygame.Rect(x, y, 50, 50)
                x += TILE_SIZE
            y += TILE_SIZE
            x = 0

    def fetch_data_server(self):
        self.player_2 = self.n.send_and_receive(self.player_1)

    def character_mechanics(self):
        player_current_pos = self.player_1.player_movement(self.walls)
        # if it's player 1, then fetch position of enemy and player
        if self.player_1.mode == 1:
            self.enemy_1.goal = player_current_pos
            self.player_1.enemy_pos = self.enemy_1.get_pos()  # returns tuple
        # if player 2, then fetch position of player 1 and enemy to player 2
        elif self.player_1.mode == 2:
            self.player_1.enemy_goal = (self.player_2.rect.x, self.player_2.rect.y)
            self.player_1.enemy_pos = self.player_2.enemy_pos

    def render_characters(self):
        # render player
        if self.player_1.mode == 1:
            self.player_1.render(self.screen, self.player1_img[self.player_1.sprite_index])
            self.player_2.render(self.screen, self.player2_img[self.player_2.sprite_index])
        else:
            self.player_1.render(self.screen, self.player2_img[self.player_1.sprite_index])
            self.player_2.render(self.screen, self.player1_img[self.player_2.sprite_index])

        # render enemy
        if self.player_1.mode == 1:
            self.enemy_1.render_enemy(self.screen, self.player_1.enemy_pos)
        else:
            self.enemy_1.render_enemy(self.screen, self.player_2.enemy_pos)

        # render target
        if self.target_down:
            # print("down: ", self.target_img_front_index)
            self.target_img_front[self.target_img_front_index].set_colorkey((255, 255, 255))
            self.screen.blit(self.target_img_front[self.target_img_front_index], (self.target_pos.x, self.target_pos.y))

        elif self.target_up:
            # print("up: ", self.target_img_back_index)
            self.target_img_back[self.target_img_back_index].set_colorkey((255, 255, 255))

            self.screen.blit(self.target_img_back[self.target_img_back_index], (self.target_pos.x, self.target_pos.y))

    def render_world(self):
        self.screen.blit(self.background, (0, 0))
        # self.draw_grid()
        for wall in self.walls:
            pygame.draw.rect(self.screen, LIGHT_GREY, wall.rect)

# m = Game()
