import pygame
import math
import sys
from pygame.locals import *

# INTIALISATION
screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
car = pygame.image.load('car.png')
track = pygame.image.load('race_track.png')
background = pygame.transform.scale(track, (screen.get_width(),screen.get_height()))
car = pygame.transform.scale(car, (50, 100))
clock = pygame.time.Clock()

try:
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joy = True
except:
    joy = False


forward_vel = 0
direction = 270

position = (700, 200)

TURN_SPEED = 5
ACCELERATION = 2
MAX_VEL = 20
MIN_VEL = -0.5 * MAX_VEL
BLACK = (0, 0, 0)
GREY = (113, 111, 112, 255)


game_running = True

while game_running:
    # wait for 30 frames per second
    clock.tick(30)
    for event in pygame.event.get():
        if hasattr(event, 'key'):
            if event.key == K_ESCAPE:
                sys.exit(0)     # quit the game
    if joy:   
        if joystick.get_axis(0) < -0.5:
            direction += TURN_SPEED
        elif joystick.get_axis(0) > 0.5:
            direction -= TURN_SPEED
        if joystick.get_button(2) == True:
            forward_vel += ACCELERATION
        if joystick.get_button(3) == True:
            forward_vel -= ACCELERATION
        
    keys = pygame.key.get_pressed()
    #print(keys)
    if keys[pygame.K_RIGHT] == True:
        print("Hi")
        direction -= TURN_SPEED
    if keys[pygame.K_LEFT] == True:
        direction += TURN_SPEED
    if keys[pygame.K_UP] == True:
        forward_vel += ACCELERATION
    if keys[pygame.K_DOWN] == True:
        forward_vel -= ACCELERATION
    if keys[pygame.K_ESCAPE] == True:
        sys.exit(0)     # quit the game

    
    # ..don't go too fast!
    if forward_vel > MAX_VEL:
        forward_vel = MAX_VEL
    elif forward_vel < MIN_VEL:
        forward_vel = MIN_VEL
        
    # .. new position based on current position, speed and direction
    x, y = position
    rad = direction * math.pi / 180
    x += forward_vel * math.sin(rad)
    y += forward_vel * math.cos(rad)
    position = (x, y)
    
    
    # RENDERING
    screen.blit(background, (0,0))
    
    
    #crashed? Then you die.
    pixel_colour = screen.get_at((int(x),int(y)))
    if not pixel_colour == GREY:
        print(pixel_colour)
        #print("You die")
        game_running = False
    else:
        print("you live")
        
    # .. rotate the car image for direction
    rotated_car = pygame.transform.rotate(car, direction)

    # .. position the car on screen
    rotated_car_rect = rotated_car.get_rect()
    rotated_car_rect.center = position

    # .. render the car to screen
    screen.blit(rotated_car, rotated_car_rect)
    pygame.display.flip()
    
print("You die")
sys.exit(0)