from typing import Type
import pygame
import math
import sys
import random
import time
import copy
import pygame.joystick
#from icecream import ic

from pygame.locals import *
fullscreen_mode = True
fullscreen_mode = not fullscreen_mode
# INTIALISATION:
if fullscreen_mode:
    SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN)
else:
    SCREEN = pygame.display.set_mode((1920 ,1080),flags = pygame.HWSURFACE)
CLOCK = pygame.time.Clock()
pygame.init()
START_TIME = time.time()

# CONSTANTS AND DEFAULT VALUES:
DEFAULT_TURN_SPEED = 5
DEFAULT_ACCELERATION = 2
DEFAULT_MAX_VEL = 20
DEFAULT_MIN_VEL = -0.5 * DEFAULT_MAX_VEL
BLACK = (0, 0, 0)
GREY = (113, 111, 112, 255)
WHITE = (255,255,255)
TRANSPARENT = (0,0,0,0)
DEFAULT_TEXT_SIZE = 20 
MAX_PLAYERS = 4
# SO WE CAN DISPLAY TEXT INFO. Set display_text and blit text in the game loop
DEFAULT_FONT = pygame.font.Font('freesansbold.ttf', DEFAULT_TEXT_SIZE)

#CLASSES:
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
            if not self.passed:
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
class Controls():
    def __init__(self, joystick:pygame.joystick.Joystick, left, right, accelerate, brake, reverse) -> None:
        self.joystick = joystick
        self.left = left
        self.right = right
        self.accelerate = accelerate
        self.brake = brake
        self.reverse = reverse
class Car(CollideItem):

    def __init__(self, image_file, x, y, width, height, velocity, direction, turn_speed, acceleration, max_vel, min_vel, name, checkpoints:list[Checkpoint], controls:Controls):
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
        self.controls = controls
    def definitely_touching(self, car):
        min_distance = min(self.rect.width,self.rect.height)/2+min(car.rect.width,car.rect.height)/2
        distance_between_centers = ((self.rect.center[0]-car.rect.center[0])**2 + (self.rect.center[1]-car.rect.center[1])**2)**0.5
        return distance_between_centers < min_distance
    def do_collision(self, car):
        """Enacts a collision between 2 cars

        Args:
            car (Car): the Other car
        """
        if self == car:
            return
        elif self.definitely_touching(car) and self.moving_towards(car):
        #elif self.collides_with(car) and self.moving_towards(car):#collides_with bad for rotated cars
            if not type(car) == Car:
                print("Not car error?")
            #print(f"Oof {self.direction} at {self.velocity}, and {car.direction} at {car.velocity}")
            # don't do collision twice!
            if self.rect.center[0] <= car.rect.center[0]:
                average_direction = (self.direction + car.direction) //2
                self.direction, car.direction = (average_direction+car.direction)//2 , (average_direction+self.direction)//2
                # reduce velocities
                self.velocity -=1
                car.velocity -=1
                #print(f"after {self.direction} at {self.velocity}, and {car.direction} at {car.velocity}")

                self.update_position()
                car.update_position()
    def moving_towards(self, other_car):
        #TODO probably should decompose next_position to method and use in update
        direction_in_radians = self.direction % 360 * math.pi / 180
        self_next_x = self.rect.x + round(self.velocity * math.sin(direction_in_radians))
        self_next_y = self.rect.x +round(self.velocity * math.cos(direction_in_radians))
        other_car_next_x = other_car.rect.x + round(other_car.velocity * math.sin(direction_in_radians))
        other_car_next_y = other_car.rect.x +round(other_car.velocity * math.cos(direction_in_radians))
        #Use Pythagoras to see if the difference between the two points will be less
        distance_next = ((self_next_x-other_car_next_x)**2 + (self_next_y-other_car_next_y)**2)**0.5
        distance_now = ((self.rect.x-other_car.rect.x)**2 + (self.rect.y-other_car.rect.y)**2)**0.5
        return distance_next < distance_now
    def react_to_keys(self, keys):
        if keys[self.controls.left]==True:
            self.turn_left()
        elif keys[self.controls.right]==True:
            self.turn_right()
        if keys[self.controls.accelerate]==True:
            self.accelerate()
        if keys[self.controls.brake]==True:
            self.brake()
        if keys[self.controls.reverse]==True:
            self.reverse()
    def turn_left(self):
        self.direction += self.turn_speed
        self.direction %= 360
    def turn_right(self):
        self.direction -= self.turn_speed
        self.direction %= 360
    def accelerate(self):
        self.velocity += self.acceleration
        if self.velocity > self.max_vel:
            self.velocity = self.max_vel
    def brake(self):
        self.velocity = self.velocity / 1.2
    def reverse(self):
        self.velocity -= self.acceleration
        if self.velocity < self.min_vel:
            self.velocity = self.min_vel
    def react_to_joystick(self):
        if self.controls.joystick.get_axis(self.controls.left) < -0.5:
            self.turn_left()
        elif self.controls.joystick.get_axis(self.controls.left) > 0.5:
            self.turn_right()
        if self.controls.joystick.get_button(self.controls.accelerate)==True:
            self.accelerate()
        if self.controls.joystick.get_button(self.controls.brake)==True:
            self.brake()
        if self.controls.joystick.get_button(self.controls.reverse)==True:
            self.reverse()     
    def react_to_controls(self, keys):
        if self.controls.joystick == None:
            self.react_to_keys(keys)
        else:
            self.react_to_joystick()
    def update_position(self):
        self.direction %= 360
        # .. new position based on current x,y, speed and direction
        direction_in_radians = self.direction * math.pi / 180
        self.rect.x += round(self.velocity * math.sin(direction_in_radians))
        self.rect.y += round(self.velocity * math.cos(direction_in_radians))
        # .. rotate the car image for direction
        self.rotated_surface = pygame.transform.rotate(
            self.surface, self.direction)
        # .. position the car on screen
        current_center = self.rect.center
        self.rect = self.rotated_surface.get_rect()
        self.rect.center = current_center
    def do_track_colour_based_update(self, display:pygame.Surface):
        """Checks the pixel colour under the centre of the car and drives horribly if it's not light grey like tarmac.

        Args:
            display (pygame.Surface): The surface to check the pixel colour of at the position of the car's rect.center
        """        
        pixel_colour = display.get_at(
            (int(self.rect.center[0]), int(self.rect.center[1])))
        red = pixel_colour[0]
        green = pixel_colour[1]
        blue = pixel_colour[2]
        if not (red in range(GREY[0]-10, GREY[0]+11) and
                green in range(GREY[1]-10, GREY[1]+11) and
                blue in range(GREY[2]-10, GREY[2]+11)):
            self.velocity = 1
    def check_checkpoints(self, race_time:int, race):
        """Update checkpoints for this car

        Args:
            race_time (int): [How long the race has been running for in seconds.]
            race (Race): [The Race object.]

        Returns:
            [type]: [description]
        """        
        for checkpoint in self.checkpoints:
            result = checkpoint.hit_checkpoint(self.direction, self.rect)          
            if result == "lap": # If the car has passed the finish line
                for other_checkpoint in self.checkpoints: # Check all checkpoints have been passed this lap
                    if not other_checkpoint.passed:
                        checkpoint.passed = False
                if checkpoint.passed == True: # It's a valip lap
                    self.laps += 1
                    lap_time = race_time - sum(self.laptimes)
                    self.laptimes.append(lap_time)
                    print(lap_time)
                    if lap_time == min(self.laptimes): # if this car's fastest lap
                        race.do_fastest_lap(self, lap_time) # see if it's the race's fastest lap
                    if self.laps == race.num_laps:
                        # Car has finished the race, so return True
                        return True
                    for any_checkpoint in self.checkpoints: #reset checkpoints for new lap
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
class Track(Sprite):
    def __init__(self, image_file, x, y, width, height, checkpoints, track_items) -> None:
        super().__init__(image_file, x, y, width, height)
        self.checkpoints = checkpoints
        self.track_items = track_items
class Race():
    def __init__(self, track:Track, cars:list[Car], num_laps:int) -> None:
        self.track = track        
        self.cars = cars        
        self.num_laps = num_laps
        #To hold [car.name:str, laptime:float]
        self.fastest_lap = []
        self.display_text = f"Laps: {self.num_laps}"
    def do_fastest_lap(self, car, laptime):
        if self.fastest_lap == [] or laptime < self.fastest_lap[1]:
            self.fastest_lap = [car.name, laptime]
            print(self.fastest_lap)
        self.display_text += f" Fastest lap {self.fastest_lap[0]} : {self.fastest_lap[1]:.2f}s "
    def do_win_screen(self, car):
        end_string = f"    !!!   {car.name} won the race in {(sum(car.laptimes)):.2f} s. (Fastest lap: {min(car.laptimes):.2f}s)    !!!"
        self.display_text += end_string

# Functions/procedures:     
def start_game_loop(screen, race, cars):
    """The main game loop of the game where all the events are responded to, objects are blitted onto the screen and other functions are called.

    Args:
        screen (pygame.Surface): The background to blit stuff onto
        race (Race): The race holds info about the race, including the track, checkpoints, num laps etc. 
        cars (list[Car]): The cars in the race
    """    
    game_running = True
    while game_running:
        # wait for 30 frames per second
        CLOCK.tick(30)
        for event in pygame.event.get():
            if hasattr(event, 'key'):
                if event.key == pygame.K_ESCAPE:
                    print("Bye")
                    sys.exit(0)     # Escape to quit the game
                elif event.key == pygame.K_DELETE:
                    pause()         # Delet to pause (escape to unpause)
        keys = pygame.key.get_pressed()


        # RENDER background
        SCREEN.blit(race.track.surface, (0, 0))

        # deal with collisions with track items like bananas and going off the grey road.
        for sprite in race.track.track_items:
            SCREEN.blit(sprite.surface, sprite.rect)
            for car in cars:
                if not sprite.do_collision(car):
                    car.do_track_colour_based_update(SCREEN)
        

        #for debugging. TODO comment out or make better
        show_checkpoints(SCREEN, race.track.checkpoints)
        
        # do other car logic like hitting other cars, reacting to controls, checking whether passed through 
        # checkpoints, updating position and direction, and blitting the rotated car to screen.
        race_time = time.time() - START_TIME
        for car in cars:
            for other_car in cars:
                car.do_collision(other_car)
            car.react_to_controls(keys)
            if car.check_checkpoints(race_time, race):
                race.do_win_screen(car)
                game_running = False
            car.update_position()
            SCREEN.blit(car.rotated_surface, car.rect)
        
        # Blit text like laps info etc
        show_text(race.display_text, SCREEN)

        pygame.display.update()

        # If race finished, wait 10 seconds for win screen to be read by players
        if not game_running:
            pygame.time.wait(8000)
def show_text(message, screen):
    text = DEFAULT_FONT.render(message, True, WHITE, BLACK)
    text.get_rect().topleft = screen.get_rect().center
    #screen.fill(BLACK)
    screen.blit(text, text.get_rect())
    pygame.display.update(text.get_rect())
def controls_setup(joysticks:list[pygame.joystick.Joystick], car, screen):
    # This feels horrible. TODO: make better
    for joystick in range(len(joysticks)):
        screen.fill(BLACK)
        show_text(f"Use joystick {joystick}? (y/n) ")
        pygame.display.update()
        valid_input_given = False
        while not valid_input_given:
            keys = pygame.event.get_pressed()
            if keys[pygame.K_n] or keys[pygame.K_y]:
                valid_input_given = True
                if keys[pygame.K_y]:
                    controls = Controls(joystick,None,None,None,None,None)
                    screen.fill(BLACK)
                    show_text("Push left", screen)
                    pygame.display.update()
                    control_found = False
                    while not control_found:
                        for i in range(joystick.get_numaxes()):
                            if joystick.get_axis(i)<-0.5:
                                controls.left = i
                                controls.right = i
                                control_found = True
                    screen.fill(BLACK)
                    show_text("Push accelerate", screen)
                    pygame.display.update()
                    control_found = False
                    while not control_found:
                        for i in range(joystick.get_numbuttons()):
                            if joystick.get_button(i) == True:
                                controls.accelerate = i
                    screen.fill(BLACK)
                    show_text("Push brake", screen)
                    pygame.display.update()
                    control_found = False
                    while not control_found:
                        for i in range(joystick.get_numbuttons()):
                            if joystick.get_button(i) == True:
                                controls.brake = i
                    screen.fill(BLACK)
                    show_text("Push reverse", screen)
                    pygame.display.update()
                    control_found = False
                    while not control_found:
                        for i in range(joystick.get_numbuttons()):
                            if joystick.get_button(i) == True:
                                controls.reverse = i
                    return

    controls = Controls(None,None,None,None,None,None)
    screen.fill(BLACK)
    show_text("Push left", screen)
    pygame.display.update()
    control_found = False
    while not control_found:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                controls.left = event.key
                control_found = True
    screen.fill(BLACK)
    show_text("Push right", screen)
    pygame.display.update()
    control_found = False
    while not control_found:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                controls.right = event.key
                control_found = True
    screen.fill(BLACK)
    show_text("Push accelerate", screen)
    pygame.display.update()
    control_found = False
    while not control_found:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:                
                controls.accelerate = event.key
                control_found = True
    screen.fill(BLACK)
    show_text("Push brake", screen)
    pygame.display.update()
    control_found = False
    while not control_found:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                controls.brake = event.key
                control_found = True
    screen.fill(BLACK)
    show_text("Push reverse", screen)
    pygame.display.update()
    control_found = False
    while not control_found:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                controls.reverse = event.key
                control_found = True
    car.controls = controls
    return
def test_joystick(joystick):
    """For command-line testing of joystick outside of game

    Args:
        joystick (pygame.joystick.Joystick): A joystick
    """    
    while not input("Press enter to test joystick or n to quit joystick test") == 'n':
        for num in range(14):
            try:
                if joystick.get_button(num):
                    print(num)
            except Exception as e:
                continue
                print(e)
def customise_controls(cars,screen):
    joysticks = []
    try:
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            joysticks.append(joystick)  
    except:
        print("No joysticks.")

    for car in cars:
        controls_setup(joysticks, car, SCREEN)
    pygame.time.wait(500)
def default_controls(cars:list[Car]):
    control_sets = [{
        'left':pygame.K_LEFT,
        'right':pygame.K_RIGHT,
        'accelerate':pygame.K_UP,
        'brake':pygame.K_SPACE,
        'reverse': pygame.K_RSHIFT
    },
    {
        'left':pygame.K_a,
        'right':pygame.K_d,
        'accelerate':pygame.K_w,
        'brake':pygame.K_s,
        'reverse': pygame.K_z
    }]
    for i in range(len(control_sets)):
        control_set = control_sets[i]
        controls = Controls(None, control_set['left'],control_set['right'],
        control_set['accelerate'], control_set['brake'],control_set['reverse'])

        cars[i].controls = controls
def pause():
    """Pauses the pygame; push escape to unpause.
    """
    paused = True
    while paused:
        pygame.time.wait(1000)
        for event in pygame.event.get():
            if hasattr(event, 'key') and event.key == pygame.K_ESCAPE: 
                paused = False
def show_checkpoints(screen, checkpoints):
    for checkpoint in checkpoints:
        pygame.draw.rect(SCREEN,(255,255,0), checkpoint.rect, 1)

#SETUP OBJECTS TODO version 2 Separate database and persistent storage of tracks and best laps etc?

#checkpoints to ensure no cheating! Rect, prefered direction (deg) finish line (bool)
checkpoints = []
CHECKPOINT_WIDTH = DEFAULT_MAX_VEL*2
checkpoints.append(Checkpoint((1300, 130, CHECKPOINT_WIDTH, 220), 270, True))
checkpoints.append(Checkpoint((0, 320, 400, CHECKPOINT_WIDTH), 0))
checkpoints.append(Checkpoint((1230, 500, 280, CHECKPOINT_WIDTH), 0))
checkpoints.append(Checkpoint((0, 780, 360, CHECKPOINT_WIDTH), 180))
checkpoints.append(Checkpoint((1540, 800, 380, CHECKPOINT_WIDTH), 180))

# cars setup
car1 = Car('car.png', 800, 180, 35, 70, 0, 270,
        DEFAULT_TURN_SPEED, DEFAULT_ACCELERATION, DEFAULT_MAX_VEL, DEFAULT_MIN_VEL, "Dave", copy.deepcopy(checkpoints),None)
car2 = Car('car2.png',800,140,30,60,0,270,DEFAULT_TURN_SPEED+1,DEFAULT_ACCELERATION+1,DEFAULT_MAX_VEL-5,DEFAULT_MIN_VEL,"Phoebe",copy.deepcopy(checkpoints),None)
cars = [car1, car2]

# track items setup
banana1 = Banana('banana.png', 600, 600, 80, 80, 2)
track_items = [banana1]

# track and race setup
track = Track('race_track.png',0,0,SCREEN.get_width(),SCREEN.get_height(),checkpoints,track_items)
race = Race(track,cars,2)

# setup controls
default_controls(cars)
customise_controls(cars, SCREEN)

start_game_loop(SCREEN, race, cars)
pygame.quit()
sys.exit(0)