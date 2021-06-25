import pygame, math, sys, random, time
from pygame.locals import *

NUM_LAPS = 1
laps = 0

class Checkpoint():
    """Checkpoint class to encapsulate info and functionality about checkpoints in a race circuit.
    """    
    def __init__(self, rect, direction, start_finish_line = False):
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
        if self.rect.colliderect(car_rect) and abs(self.direction%360-direction%360)<90:
            self.passed = True
        if self.start_finish_line == True:
            return "lap"
        else:
            return "checkpoint"


# INTIALISATION
SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN)

car = pygame.image.load('car.png')
track = pygame.image.load('race_track.png')
background = pygame.transform.scale(track, (SCREEN.get_width(),SCREEN.get_height()))
car = pygame.transform.scale(car, (50, 100))
clock = pygame.time.Clock()

#setup a banana as an obstacle
banana = pygame.image.load('banana.png')
banana_x = 600
banana_y = 600
banana_width = 80
banana_height = 80
banana = pygame.transform.scale(banana, (banana_width, banana_height))
banana_rect = pygame.Rect((banana_x, banana_y), (banana_width, banana_height))
banana_slippiness = 2

banana1 = Banana('banana.png', 600, 600, 80, 80, 2)

class TrackItem():
    def TrackItem(self, image_file, x, y, width, height):
        self.image_file = image_file
        self.rect = pygame.Rect(x, y, width, height)
        

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


checkpoints = []
checkpoints.append(Checkpoint((800,150,MAX_VEL+1,200), 270, True))
checkpoints.append(Checkpoint((400,150,MAX_VEL+1,200), 270))

start_time = time.time()

game_running = True

def test_joy():
    for num in range(10):
        if joystick.get_button(num):
            print(num)


while game_running:
    # wait for 30 frames per second
    clock.tick(30)
    for event in pygame.event.get():
        if hasattr(event, 'key'):
            if event.key == pygame.K_ESCAPE:
                print("Bye")
                sys.exit(0)     # quit the game
    if joy:
        test_joy()
        if joystick.get_axis(0) < -0.5:
            #turn left
            direction += TURN_SPEED
        elif joystick.get_axis(0) > 0.5:
            #turn right
            direction -= TURN_SPEED
        if joystick.get_button(2) == True:
            #accelerate
            forward_vel += ACCELERATION
        if joystick.get_button(3) == True:
            #reverse
            forward_vel -= ACCELERATION
        if joystick.get_button(5) == True:
            #brake
            forward_vel =  forward_vel / 1.2
        
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
    if keys[pygame.K_SPACE] == True:
        #brake
        forward_vel =  forward_vel / 1.2
    
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
    
    
    # RENDERING images to the screen using the blit function
    SCREEN.blit(background, (0,0))
    SCREEN.blit(banana, banana_rect)
    
    car_rect = (x, y, car.get_width(), car.get_height())
    
    if banana_rect.colliderect(car_rect):
        direction += random.randint(-banana_slippiness,banana_slippiness)
    else:
        #crashed? Then you die.
        pixel_colour = SCREEN.get_at((int(x),int(y)))
        red = pixel_colour[0]
        green = pixel_colour[1]
        blue = pixel_colour[2]
        if not (red in range(GREY[0]-10,GREY[0]+11) and 
                green in range(GREY[1]-10,GREY[1]+11) and 
                blue in range(GREY[2]-10,GREY[2]+11)):
            print(pixel_colour)
            print("You die")
            position = (700,200)
            forward_vel = 0
            direction = 270
            
    for checkpoint in checkpoints:
        result = checkpoint.hit_checkpoint(direction,(car_rect))
        if result == "lap":
            for other_checkpoint in checkpoints:
                if not other_checkpoint.passed:
                    checkpoint.passed = False
            if checkpoint.passed == True:
                laps += 1
                print("LAP!", laps)
                if laps == NUM_LAPS:
                    end_time = time.time()
                    print("You completed the course in:", end_time - start_time)
                    pygame.time.delay(2000)
                    game_running = False
                for any_checkpoint in checkpoints:
                    any_checkpoint.passed = False

    # .. rotate the car image for direction
    rotated_car = pygame.transform.rotate(car, direction)
    # .. position the car on screen
    rotated_car_rect = rotated_car.get_rect()
    rotated_car_rect.center = position

    # .. render the car to screen
    SCREEN.blit(rotated_car, rotated_car_rect)
    pygame.display.flip()
    
sys.exit(0)