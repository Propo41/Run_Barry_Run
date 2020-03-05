import os
import sys

import pygame

from Game import Game
from network import Network
from util import SCREEN_WIDTH, SCREEN_HEIGHT, load_image, CLOCK, FPS, EXIT, START, button_mechanics

FLASH_LOGO_BLINK_INTERVAL = pygame.USEREVENT + 3
pygame.time.set_timer(FLASH_LOGO_BLINK_INTERVAL, 500)


class Button:
    def __init__(self, img_address, img_address_clicked, topleft_x, topleft_y, state):
        self.x = topleft_x
        self.y = topleft_y
        self.hovered = False
        self.img = load_image(img_address)
        self.img_hovered = load_image(img_address_clicked)
        self.rect = self.img.get_rect(topleft=(topleft_x, topleft_y))
        self.rect_hovered = self.img_hovered.get_rect(topleft=(topleft_x, topleft_y))
        self.state = state


class Start_Game:
    def __init__(self):
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # window navigation variables
        self.is_connecting_screen = False
        self.is_loading_screen = False
        self.start_game = False

        self.all_buttons = []
        self.init_buttons()

        self.home_screen = pygame.image.load("Assets/background/home_screen.png").convert()
        # 0: loading screen
        # 1: loading screen animation icon
        self.connecting_screen = [pygame.image.load("Assets/background/loading_screen.png").convert(),
                                  pygame.image.load("Assets/background/loading_screen_animation.png").convert()]
        self.loading_screen = [pygame.image.load("Assets/background/p1_loading.png").convert(),
                               pygame.image.load("Assets/background/p2_loading.png").convert()]

        self.blink_flash_logo = False

        # delay counter used to halt the loading screen for a few seconds
        self.delay = 0
        self.delay_param = 200

        self.n = Network()
        self.player_1 = self.n.fetch_initial_data()

        self.interface_loop()  # interface menu
        Game(self.n, self.player_1, self.player_2)  # after both players are connected, the game starts

    def init_buttons(self):
        self.all_buttons.append(Button('Assets/background/START_1.png', 'Assets/background/START_2.png', 564, 156, 1))
        self.all_buttons.append(Button('Assets/background/exit_1.png', 'Assets/background/exit_2.png', 608, 536, 2))

    def interface_loop(self):
        while not self.start_game:
            CLOCK.tick(FPS)
            # gets data from server and if both players are connected, continues to next window
            self.fetch_data_server()
            self.event_handling()
            button_mechanics(self.all_buttons)
            self.display()

    def check_hovered_state(self, buttons_list):
        # iterates through the buttons list and checks which buttons are clicked
        for img in buttons_list:  # check which buttons are in hovered state
            if img.hovered:
                if img.state == START:  # move to the desired window
                    self.is_connecting_screen = True
                    self.player_1.is_start_clicked = True

                elif img.state == EXIT:
                    sys.exit(0)

    def fetch_data_server(self):
        self.player_2 = self.n.send_and_receive(self.player_1)
        if self.player_1.is_start_clicked and self.player_2.is_start_clicked:
            self.is_loading_screen = True
            self.is_connecting_screen = False

    def event_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            # if mouse cursor within START or EXIT text, then change the icon
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                # print(pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # if left button pressed
                    # check which buttons are in hovered state
                    self.check_hovered_state(self.all_buttons)
            if event.type == FLASH_LOGO_BLINK_INTERVAL:
                self.blink_flash_logo = not self.blink_flash_logo

    def display(self):
        if self.is_connecting_screen:
            if self.blink_flash_logo:
                self.connecting_screen[1].set_colorkey((255, 255, 255))
                self.screen.blit(self.connecting_screen[1], (571, 270))
            else:
                self.screen.blit(self.connecting_screen[0], (0, 0))
        elif self.is_loading_screen:
            self.delay += 1
            if self.delay >= self.delay_param:
                self.start_game = True
            if self.player_1.mode == 1:
                self.screen.blit(self.loading_screen[0], (0, 0))
            elif self.player_1.mode == 2:
                self.screen.blit(self.loading_screen[1], (0, 0))

        else:
            self.screen.blit(self.home_screen, (0, 0))
            # check button hovered state
            for i in self.all_buttons:
                if i.hovered:
                    i.img_hovered.set_colorkey((0, 0, 0))
                    self.screen.blit(i.img_hovered, (i.x, i.y))
                else:
                    i.img.set_colorkey((0, 0, 0))
                    self.screen.blit(i.img, (i.x, i.y))

        pygame.display.update()


a = Start_Game()
