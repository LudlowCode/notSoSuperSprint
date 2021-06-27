import pygame
import math
import sys
import random
import time
from pygame.locals import *

# INTIALISATION
#SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN)
SCREEN = pygame.display.set_mode((1600,1200))
CLOCK = pygame.time.Clock()
pygame.init()
game_running = True
START_TIME = time.time()

# constants
TURN_SPEED = 5
ACCELERATION = 2
MAX_VEL = 20
MIN_VEL = -0.5 * MAX_VEL
BLACK = (0, 0, 0)
GREY = (113, 111, 112, 255)


class Checkpoint():
    """Checkpoint class to encapsulate info and functionality about checkpoints in a race circuit.
    """

    def __init__(self, rect, direction, start_finish_line=False):
        """Constructor for a checkpoint.

        Args:
            rect (pygame.Rect): Holds the pygame.Rect that has x, y, width, height of the checkpoint.
            direction (int): The optimal angle to pass through the checkpoint. A pass through that is > 90 deg different won't cound
            start_finish_line (bool, optional): Whether the checkpoint is the S/F line. Defaults to False.
        """
        self.rect = pygame.Rect(rect)
        self.direction = direction
        self.passed = False
        self.start_finish_line = start_finish_line

    def hit_checkpoint(self, direction, car_rect):
        """Checks whether hte car has passed through the checkpoint. Stes passed to true if car has passed throgh in the 
        correct direction.

        Args:
            direction (int): Angle in degrees the car is travelling
            car_rect (pygame.Rect): Rect of the car.

        Returns:
            String: Whether the checkpoint is a normal one or a lap
        """
        # Mod to ignore any situation where angle somehow becomes over 360. Abs to just check the difference between the
        # two angles; over 90 deg difference means the checkpoint has been passed the wrong way.
        if self.rect.colliderect(car_rect) and abs(self.direction % 360-direction % 360) < 90:
            self.passed = True
        if self.start_finish_line == True:
            return "lap"
        else:
            return "checkpoint"


class Sprite():
    def __init__(self, image_file, x, y, width, height):
        self.surface = pygame.image.load(image_file)
        self.surface = pygame.transform.scale(self.surface, (width, height))
        self.rect = pygame.Rect(x, y, width, height)


class CollideItem(Sprite):
    def __init__(self, image_file, x, y, width, height):
        super().__init__(image_file, x, y, width, height)

    def collides_with(self, item):
        if self.rect.colliderect(item.rect):
            return True
        else:
            return False


class Car(CollideItem):
    def __init__(self, image_file, x, y, width, height, velocity, direction, turn_speed, acceleration, max_vel, min_vel, laptimes=[]):
        super().__init__(image_file, x, y, width, height)
        self.velocity = velocity
        self.direction = direction
        self.turn_speed = turn_speed
        self.acceleration = acceleration
        self.max_vel = max_vel
        self.min_vel = min_vel
        self.laptimes = laptimes
        self.rotated_surface = self.surface
        self.rect = self.rotated_surface.get_rect(topleft = (x, y))
        print(self.rotated_surface)

    def do_collision(self, car):
        """Enacts a collision between 2 cars

        Args:
            car (Car): the Other car
        """
        if self.collides_with(car):
            if not type(car) == Car:
                print("Not car error?")
            print("Oof")
            # don't do collision twice!
            if self.x <= car.x:
                # swap directions
                self.direction, car.direction = car.direction, car.direction
                # reduce velocities
                self.velocity *= 0.5
                car.velocity *= 0.5
    def update_position(self):
        # .. new position based on current x,y, speed and direction
        direction_in_radians = self.direction * math.pi / 180
        self.rect.x += self.velocity * math.sin(direction_in_radians)
        self.rect.y += self.velocity * math.cos(direction_in_radians)
        # .. rotate the car image for direction
        self.rotated_surface = pygame.transform.rotate(self.surface, car1.direction)
        # .. position the car on screen
        #self.rect = self.rotated_surface.get_rect()
        #self.rect.center = (self.rect.x, self.rect.y)
    def blit(self, display):
        display.blit(self.rotated_surface, self.rotated_surface.get_rect())
class Banana(CollideItem):
    def __init__(self, image_file, x, y, width, height, slippiness):
        super().__init__(image_file, x, y, width, height)
        self.slippiness = slippiness

    def do_collision(self, car):
        if self.collides_with(car):
            car.direction += random.randint(-self.slippiness, -self.slippiness)


# car setup
car1 = Car('car.png', 700, 200, 50, 100, 0, 270,
           TURN_SPEED, ACCELERATION, MAX_VEL, MIN_VEL)
#blit_rect = car1.rotated_surface.get_rect()


# setup a banana obstacle
banana1 = Banana('banana.png', 600, 600, 80, 80, 2)

# track stuff TODO OOP it
NUM_LAPS = 3
laps = 0
track = pygame.image.load('race_track.png')
track = pygame.transform.scale(
    track, (SCREEN.get_width(), SCREEN.get_height()))



try:
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joy = True
except:
    joy = False


checkpoints = []
checkpoints.append(Checkpoint((800, 150, MAX_VEL+1, 200), 270, True))
checkpoints.append(Checkpoint((400, 150, MAX_VEL+1, 200), 270))

def do_fastest_lap(car, laptime):
    print(car.name, "has the new fastest lap of", laptime, 'seconds!')



def test_joy():
    while not input("Press enter to test joystick or n to quit joystick test")=='n':
        for num in range(14):
            try:
                if joystick.get_button(num):
                    print(num)
            except Exception as e:
                continue
                print(e)

if joy:
    test_joy()

while game_running:
    # wait for 30 frames per second
    CLOCK.tick(30)
    for event in pygame.event.get():
        if hasattr(event, 'key'):
            if event.key == pygame.K_ESCAPE:
                print("Bye")
                sys.exit(0)     # quit the game
    if joy:
        
        if joystick.get_axis(0) < -0.5:
            # turn left
            car1.direction += TURN_SPEED
        elif joystick.get_axis(0) > 0.5:
            # turn right
            car1.direction -= TURN_SPEED
        if joystick.get_button(2) == True:
            # accelerate
            car1.velocity += ACCELERATION
        if joystick.get_button(3) == True:
            # reverse
            car1.velocity -= ACCELERATION
        if joystick.get_button(5) == True:
            # brake
            car1.velocity = car1.velocity / 1.2

    keys = pygame.key.get_pressed()
    # print(keys)
    if keys[pygame.K_RIGHT] == True:
        print("Hi")
        car1.direction -= TURN_SPEED
    if keys[pygame.K_LEFT] == True:
        car1.direction += TURN_SPEED
    if keys[pygame.K_UP] == True:
        car1.velocity += ACCELERATION
    if keys[pygame.K_DOWN] == True:
        car1.velocity -= ACCELERATION
    if keys[pygame.K_SPACE] == True:
        # brake
        car1.velocity = car1.velocity / 1.2

    # ..don't go too fast!
    if car1.velocity > MAX_VEL:
        car1.velocity = MAX_VEL
    elif car1.velocity < MIN_VEL:
        car1.velocity = MIN_VEL




    # RENDERING images to the screen using the blit function
    SCREEN.blit(track, (0, 0))
    SCREEN.blit(banana1.surface, banana1.rect)

    #banana1.do_collision(car1)

    # crashed? Then you die.
    pixel_colour = SCREEN.get_at((int(car1.rect.x), int(car1.rect.y)))
    red = pixel_colour[0]
    green = pixel_colour[1]
    blue = pixel_colour[2]
    if not (red in range(GREY[0]-10, GREY[0]+11) and
            green in range(GREY[1]-10, GREY[1]+11) and
            blue in range(GREY[2]-10, GREY[2]+11)):
        print(pixel_colour)
        print("You die")
        position = (700, 200)
        car1.rect.x, car1.rect.y = 700, 200
        car1.velocity = 0
        car1.direction = 270

    for checkpoint in checkpoints:
        result = checkpoint.hit_checkpoint(car1.direction, car1.rect)
        if result == "lap":
            for other_checkpoint in checkpoints:
                if not other_checkpoint.passed:
                    checkpoint.passed = False
            if checkpoint.passed == True:
                laps += 1
                print("LAP!", laps)
                now = time.time()
                lap_time = now - sum(car1.laptimes)
                car1.laptimes.append(lap_time)
                if lap_time == min(car1.laptimes):
                    do_fastest_lap(car1, lap_time)
                if laps == NUM_LAPS:
                    print("You completed the course in:", now - START_TIME)
                    pygame.time.delay(2000)
                    game_running = False
                for any_checkpoint in checkpoints:
                    any_checkpoint.passed = False
            

    

    # .. render the car to screen
    car1.update_position()
    #car1.blit(SCREEN)
    #blit_rect = car1.rotated_surface.get_rect()
    SCREEN.blit(car1.rotated_surface, car1.rect)
    pygame.display.flip()

sys.exit(0)
