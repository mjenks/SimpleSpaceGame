'''
Simple game controlling a spaceship to collect items

Author: mjenks
'''

from email.header import Header
from readline import get_current_history_length
import pygame
import os
import random

#Colors
WHITE = (255,255,255)

#Constants
SIZE = WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode(SIZE)
BKGD_SIZE = BKGD_WIDTH, BKGD_HEIGHT = 1800, 500
SHIP_IMAGE_SIZE = 200, 300
SHIP_SIZE = SHIP_WIDTH, SHIP_HEIGHT = 100, 100
STAR_SIZE = STAR_WIDTH, STAR_HEIGHT = 30, 30

FPS = 60
PAD = 25

BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'purple_space_background.png')),BKGD_SIZE).convert()
SHIP_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'ship.png')), SHIP_IMAGE_SIZE).convert_alpha()
GREEN_STAR = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'green_star.png')), STAR_SIZE).convert_alpha()
RED_STAR = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'red_star.png')), STAR_SIZE).convert_alpha()

#Fonts
pygame.font.init()
STATS_FONT = pygame.font.SysFont('comicsans', 20)
WIN_FONT = pygame.font.SysFont('halvetica', 80)

#Events
PLAYER_WIN = pygame.USEREVENT + 1

#Classes
class Ship(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()     
        self.index = 0
        self.sheet = image
        self.area = pygame.Rect(0,0,SHIP_WIDTH,SHIP_HEIGHT)
        self.image = self.sheet.subsurface(self.area)
        self.rect = self.image.get_rect()
        self.moving = False
        self.acceleration = 0
        self.rect.topleft = pos
        self.vel = 5

    def update(self):
        if self.acceleration == -1:
            self.index += .2
            if self.index >= 2:
                self.index = 0
                self.area = pygame.Rect(0,0,SHIP_WIDTH,SHIP_HEIGHT)
                self.image = self.sheet.subsurface(self.area)
                self.acceleration = 0
                self.moving = False
            else:
                self.area = pygame.Rect(SHIP_WIDTH*(1-int(self.index)),SHIP_HEIGHT,SHIP_WIDTH,SHIP_HEIGHT)
                self.image = self.sheet.subsurface(self.area)
        elif self.acceleration == 1:
            self.index += .2
            if self.index >= 2:
                self.index = 0
                self.area = pygame.Rect(0,2*SHIP_HEIGHT, SHIP_WIDTH,SHIP_HEIGHT)
                self.image = self.sheet.subsurface(self.area)
                self.acceleration = 0
                self.moving = True
            else:
                self.area = pygame.Rect(SHIP_WIDTH*int(self.index),SHIP_HEIGHT,SHIP_WIDTH,SHIP_HEIGHT)
                self.image = self.sheet.subsurface(self.area)
        elif self.moving: 
            self.index += .1
            if self.index >= 2:
                self.index = 0
            self.area = pygame.Rect(SHIP_WIDTH*int(self.index),2*SHIP_HEIGHT,SHIP_WIDTH,SHIP_HEIGHT)
            self.image = self.sheet.subsurface(self.area)
        else:
            self.index = 0
            self.area = pygame.Rect(0,0,SHIP_WIDTH,SHIP_HEIGHT)
            self.image = self.sheet.subsurface(self.area)

    def move(self, keys_pressed):
        if keys_pressed[pygame.K_UP] and self.rect.y - self.vel > 0:
            self.rect.y -= self.vel
        if keys_pressed[pygame.K_DOWN] and self.rect.y + self.vel + SHIP_HEIGHT < HEIGHT:
            self.rect.y += self.vel
        if keys_pressed[pygame.K_LEFT] and self.rect.x - self.vel > 0 and self.moving:
            self.rect.x -= self.vel
        if keys_pressed[pygame.K_RIGHT] and self.rect.x + self.vel < WIDTH//2 and self.moving:
            self.rect.x += self.vel

class Star(pygame.sprite.Sprite):
    def __init__(self, color, pos, moving):
        super().__init__() 
        self.color = color
        if color == 'green':
            self.base_image = GREEN_STAR
            self.vel = 3
        elif color == 'red':
            self.base_image = RED_STAR
            self.vel = 5
        else:
            self.base_image = GREEN_STAR
            self.vel = 10
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.moving = moving
        self.rect.topleft = pos
        self.angle = 0

    def update(self):
        #this rotates the star but also causes a wiggle
        self.angle += 1
        if self.angle == 360:
            self.angle = 0
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        if self.moving:
            self.rect.x -= self.vel   
        
        

class Background(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.full_image = image
        self.x = 0
        self.area = pygame.Rect(self.x,0,WIDTH,HEIGHT)
        self.image = self.full_image.subsurface(self.area)
        self.rect = self.image.get_rect()
        self._layer = -1
        self.moving = False
        self.vel = 8

    def update(self):
        if self.moving:
            self.x += self.vel
            if self.x >= WIDTH:
                self.x -= WIDTH
            self.area = pygame.Rect(self.x,0,WIDTH,HEIGHT)
            self.image = self.full_image.subsurface(self.area)


class Enviorment(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.moving = False

    def toggle_movement(self):
        self.moving = not self.moving
        for sprite in self.sprites():
            sprite.moving = self.moving

class Collectables(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)


class PlayerShips(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)

    def toggle_movement(self):
        for sprite in self.sprites():
            if not sprite.moving:
                sprite.acceleration = 1
            if sprite.moving:
                sprite.acceleration = -1

    def movement(self, keys_pressed):
        for sprite in self.sprites():
            sprite.move(keys_pressed)

    
#functions
def update_text(stars_collected):
    stars_text = STATS_FONT.render("Stars Collected: " + str(stars_collected), 1, WHITE)
    WIN.blit(stars_text, (PAD//2, PAD//2))

def display_win():
    win_text = WIN_FONT.render("YOU WIN!!", 1, WHITE)
    WIN.blit(win_text, ((WIDTH - win_text.get_width())//2, (HEIGHT-win_text.get_height())//2))
    pygame.display.update()
    pygame.time.delay(5000)


def main():

    run = True
    clock = pygame.time.Clock()
    background = Background(BACKGROUND_IMAGE)
    ship = Ship((PAD,(HEIGHT-SHIP_HEIGHT)//2), SHIP_IMAGE)
    all_sprites = pygame.sprite.Group(background, ship)
    player = PlayerShips(ship)
    field = Enviorment(background)
    objects = Collectables()
    moving = False
    stars_collected = 0
    frames = 0
    while run:
        clock.tick(FPS)
        frames += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE):
                    player.toggle_movement()
                    field.toggle_movement()
                    moving = not moving

            if event.type == PLAYER_WIN:
                print("win")
                display_win()
                run = False
                    

        keys_pressed = pygame.key.get_pressed()
        player.movement(keys_pressed)

        if frames%100 == 0:
            if moving:
                y = random.randint(PAD, HEIGHT-2*PAD)
                green_star = Star('green', (WIDTH+2*PAD, y), moving)
                objects.add(green_star)
                all_sprites.add(green_star)
                field.add(green_star)
        if frames > 500:
            if moving:
                y = random.randint(PAD, HEIGHT-2*PAD)
                red_star = Star('red', (WIDTH+2*PAD, y), moving)
                objects.add(red_star)
                all_sprites.add(red_star)
                field.add(red_star)
            frames = 0

        collisions = pygame.sprite.groupcollide(player, objects, False, True)
        for hit in collisions.values():
            for s in hit:
                if s.color == 'green':
                    stars_collected += 1
                elif s.color == 'red':
                    stars_collected += 5
        if stars_collected >= 50:
            pygame.event.post(pygame.event.Event(PLAYER_WIN))


        all_sprites.update()
        all_sprites.draw(WIN)
        update_text(stars_collected)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    pygame.init()
    main()

