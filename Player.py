import pygame

# https://stackoverflow.com/questions/47391774/python-send-and-receive-objects-through-sockets/47396267
# surface objects cannot be sent across server with pickle
from util import make_vector, SCREEN_RECT


class Player:
    def __init__(self, x, y, mode):
        self.velocity = 2
        self.mode = mode
        self.rect = pygame.Rect(x, y, 55, 55)
        self.sprite_index = 12
        self.sprite_index_all = [0, 4, 8, 12]  # left, right, up, down
        # when sprite becomes stationary, the character index changes to 12. This variable is used for that
        self.elapsed = 0
        self.enemy_pos = None  # doesnt matter what it is, as when the server starts, it's going to be filled

    # updates each frame in the sprite to create an animation
    def update(self, dir):
        if dir == "left":
            self.sprite_index_all[0] += 1
            if self.sprite_index_all[0] > 3:
                self.sprite_index_all[0] = 0
            self.sprite_index = self.sprite_index_all[0]

        elif dir == "right":
            self.sprite_index_all[1] += 1
            if self.sprite_index_all[1] > 7:
                self.sprite_index_all[1] = 4
            self.sprite_index = self.sprite_index_all[1]

        elif dir == "up":
            self.sprite_index_all[2] += 1
            if self.sprite_index_all[2] > 11:
                self.sprite_index_all[2] = 8
            self.sprite_index = self.sprite_index_all[2]

        elif dir == "down":
            self.sprite_index_all[3] += 1
            if self.sprite_index_all[3] > 15:
                self.sprite_index_all[3] = 12
            self.sprite_index = self.sprite_index_all[3]

        elif dir == "reset":  # reset all pointers
            self.sprite_index_all[0] = 0  # start of left sprite
            self.sprite_index_all[1] = 4  # start of right sprite
            self.sprite_index_all[2] = 8  # start of up sprite
            self.sprite_index_all[3] = 12  # start of down sprite
            self.sprite_index = 12

    def move(self, dx, dy, walls):
        # print("self.rect.pos: ", self.rect.x, self.rect.y)
        self.rect.x += dx
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.rect.x -= dx
                self.rect.y -= dy
        # add code for boundary condition
        self.rect.clamp_ip(SCREEN_RECT)
        return make_vector((self.rect.x, self.rect.y))

    # returns the final position of the player after calculating wall collisions in vector form
    def player_movement(self, walls):
        key = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if key[pygame.K_LEFT]:
            dx = -self.velocity
            self.update("left")
        elif key[pygame.K_RIGHT]:
            dx = self.velocity
            self.update("right")
        elif key[pygame.K_UP]:
            dy = -self.velocity
            self.update("up")
        elif key[pygame.K_DOWN]:
            dy = self.velocity
            self.update("down")
        else:
            self.elapsed += 1
            if self.elapsed > 5:
                self.elapsed = 0
                self.update("reset")

        return self.move(dx, dy, walls)

    def set_enemy_goal(self, pos):
        self.enemy_goal = pos

    def render(self, screen, img):
        screen.blit(img, (self.rect.x, self.rect.y))
