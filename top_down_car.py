import pygame
import math
import sys
import random
import time
import copy

from pygame.locals import *

# INTIALISATION
SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN)
#SCREEN = pygame.display.set_mode((1900,1000))
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
WHITE = (255,255,255)
TRANSPARENT = (0,0,0,0)
DEFAULT_TEXT_SIZE = 20

display_text = "Not-So-Super Sprint"

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
    """Holds surface and rect that relate to a pygame actor.
    """

    def __init__(self, image_file, x, y, width, height):
        self.surface = pygame.image.load(image_file)
        self.surface = pygame.transform.scale(self.surface, (width, height))
        self.rect = pygame.Rect(x, y, width, height)


class CollideItem(Sprite):
    """Subclass of Sprite that has behaviour related to collisions with other CollideItems

    Args:
        Sprite (Sprite): Superclass.
    """

    def __init__(self, image_file, x, y, width, height):
        super().__init__(image_file, x, y, width, height)

    def collides_with(self, item):
        if self.rect.colliderect(item.rect):
            return True
        else:
            return False


class Car(CollideItem):

    def __init__(self, image_file, x, y, width, height, velocity, direction, turn_speed, acceleration, max_vel, min_vel, name, checkpoints):
        super().__init__(image_file, x, y, width, height)
        self.velocity = velocity
        self.direction = direction
        self.turn_speed = turn_speed
        self.acceleration = acceleration
        self.max_vel = max_vel
        self.min_vel = min_vel
        self.laps = 0
        self.laptimes = []
        self.rotated_surface = self.surface
        self.rect = self.rotated_surface.get_rect(topleft=(x, y))
        self.name = name
        self.checkpoints = checkpoints

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
        direction_in_radians = self.direction % 360 * math.pi / 180
        self.rect.x += round(self.velocity * math.sin(direction_in_radians))
        self.rect.y += round(self.velocity * math.cos(direction_in_radians))
        # .. rotate the car image for direction
        self.rotated_surface = pygame.transform.rotate(
            self.surface, car1.direction)
        # .. position the car on screen
        current_center = self.rect.center
        # current_x = self.rect.x
        # current_y = self.rect.y
        self.rect = self.rotated_surface.get_rect()
        # self.rect.x = current_x
        # self.rect.y = current_y
        self.rect.center = current_center

    def do_track_colour_based_update(self, display):
        pixel_colour = display.get_at(
            (int(self.rect.center[0]), int(self.rect.center[1])))
        red = pixel_colour[0]
        green = pixel_colour[1]
        blue = pixel_colour[2]
        if not (red in range(GREY[0]-10, GREY[0]+11) and
                green in range(GREY[1]-10, GREY[1]+11) and
                blue in range(GREY[2]-10, GREY[2]+11)):

            self.velocity = 1
            #self.direction = 270

    def check_checkpoints(self, start_time, now_time, race_time):
        for checkpoint in self.checkpoints:
            result = checkpoint.hit_checkpoint(self.direction, self.rect)
            if result == "lap":
                for other_checkpoint in self.checkpoints:
                    if not other_checkpoint.passed:
                        checkpoint.passed = False
                if checkpoint.passed == True:
                    self.laps += 1
                    lap_time = race_time - sum(self.laptimes)
                    self.laptimes.append(lap_time)
                    if lap_time == min(self.laptimes):
                        do_fastest_lap(self, lap_time)
                    if self.laps == NUM_LAPS:
                        # Race is complete so return True
                        return True

                    for any_checkpoint in self.checkpoints:
                        any_checkpoint.passed = False
        # False means race isn't over
        return False

    def blit(self, display):
        display.blit(self.rotated_surface, self.rotated_surface.get_rect())


class Banana(CollideItem):

    def __init__(self, image_file, x, y, width, height, slippiness):
        super().__init__(image_file, x, y, width, height)
        self.slippiness = slippiness

    def do_collision(self, car):
        if self.collides_with(car):
            car.direction += random.randint(-self.slippiness, -self.slippiness)
            return True
        else:
            return False

# SO WE CAN DISPLAY TEXT INFO. Set display_text and blit text in the game loop
font = pygame.font.Font('freesansbold.ttf', DEFAULT_TEXT_SIZE)

#checkpoints to ensure no cheating!
checkpoints = []
checkpoints.append(Checkpoint((800, 150, MAX_VEL+1, 200), 270, True))
checkpoints.append(Checkpoint((400, 150, MAX_VEL+1, 200), 270))

# car setup
car1 = Car('car.png', 700, 150, 50, 100, 0, 270,
           TURN_SPEED, ACCELERATION, MAX_VEL, MIN_VEL, "Dave", copy.deepcopy(checkpoints))

# setup a banana obstacle
banana1 = Banana('banana.png', 600, 600, 80, 80, 2)

# track stuff TODO OOP it
NUM_LAPS = 2
laps = 0
track = pygame.image.load('race_track.png')
track = pygame.transform.scale(
    track, (SCREEN.get_width(), SCREEN.get_height()))
display_text = f"Laps: {NUM_LAPS} "

def do_fastest_lap(car, laptime):
    global display_text
    display_text += f" Fastest lap {car.name} : {laptime:.2f}s "

def do_win_screen(car):
    global display_text
    end_string = f"{car.name} won the race in {(sum(car.laptimes)):.2f} s. (Fastest lap: {min(car.laptimes):.2f}s) "
    display_text += end_string


def test_joy(joystick):
    while not input("Press enter to test joystick or n to quit joystick test") == 'n':
        for num in range(14):
            try:
                if joystick.get_button(num):
                    print(num)
            except Exception as e:
                continue
                print(e)


try:
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joy = True
except:
    joy = False

if joy:
    test_joy(joystick)

while game_running:
    # wait for 30 frames per second
    CLOCK.tick(30)
    for event in pygame.event.get():
        if hasattr(event, 'key'):
            if event.key == pygame.K_ESCAPE:
                print("Bye")
                sys.exit(0)     # quit the game'''
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

    if keys[pygame.K_ESCAPE] == True:
        game_running = False     # quit the game
        break
    if keys[pygame.K_RIGHT] == True:
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
    # ..don't go too fast forwards!
    if car1.velocity > MAX_VEL:
        car1.velocity = MAX_VEL
    # or in reverse!
    elif car1.velocity < MIN_VEL:
        car1.velocity = MIN_VEL

    # RENDERING images to the screen using the blit function
    SCREEN.blit(track, (0, 0))
    SCREEN.blit(banana1.surface, banana1.rect)

    if not banana1.do_collision(car1):
        car1.do_track_colour_based_update(SCREEN)

    now = time.time()
    race_time = now - START_TIME
    if car1.check_checkpoints(START_TIME, now, race_time):
        do_win_screen(car1)
        game_running = False

    car1.update_position()
    text = font.render(display_text, True, WHITE, TRANSPARENT)
    text.get_rect().topleft = (0,0)
    SCREEN.blit(car1.rotated_surface, car1.rect)
    SCREEN.blit(text, text.get_rect())

    pygame.display.flip()
    if not game_running:
        pygame.time.wait(10000)
pygame.quit()
sys.exit(0)
