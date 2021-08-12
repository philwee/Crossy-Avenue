import random
import os
add_library('minim')

path = os.getcwd()
player = Minim(this)

NUM_COLS = 9
NUM_ROWS = 10
ROW_HEIGHT = 80
COL_WIDTH = 80
GAME_WIDTH = NUM_COLS * COL_WIDTH
GAME_HEIGHT = NUM_ROWS * ROW_HEIGHT
terrain_types = ["road", "road", "road", "water", "grass", "grass"]
terrain_types_nowater = ["road", "road", "grass", "grass", "grass"]

#pre-loading images and music since loadImage causes lag under display()
bgmusic = player.loadFile(path + "/sounds/background.mp3")
bounce = player.loadFile(path + "/sounds/bounce.wav")

road_images = []
for img in range(1,4):
    loadedimg = loadImage(path + "/images/" + "road" + str(img) + ".png")
    road_images.append(loadedimg)

water_images = []
for img in range(1,4):
    loadedimg = loadImage(path + "/images/" + "water" + str(img) + ".png")
    water_images.append(loadedimg)
    
grass_images = []
for img in range(1,4):
    loadedimg = loadImage(path + "/images/" + "grass" + str(img) + ".png")
    grass_images.append(loadedimg)

car_images = []
for img in range(1,4):
    loadedimg = loadImage(path + "/images/" + "car" + str(img) + ".png")
    car_images.append(loadedimg)
    
bee_image = loadImage(path + "/images/" + "bee" + ".png")

lilypad_images = []
for img in range(1,4):
    loadedimg = loadImage(path + "/images/" + "lilypad" + str(img) + ".png")
    lilypad_images.append(loadedimg)

bush_images = []
for img in range(1,4):
    loadedimg = loadImage(path + "/images/" + "bush" + str(img) + ".png")
    bush_images.append(loadedimg)

butterfly_images = []
butterfly_directions = ["f","b","l","r"]
for direction in butterfly_directions:
    loadedimg = loadImage(path + "/images/" + "butterfly" + direction + ".png")
    butterfly_images.append(loadedimg)
    
high_score = [] #retrieving high scores from txt file
highscores = open("high_scores.txt","r") # high_scores is a text file
for i in highscores:
    high_score.append(i.strip())
highscores.close()
    
class Gameboard:

    def __init__(self):
        self.state = True  # is the game active
        # list of terrain objects, last object is the highest in the board
        self.terrain_list = []
        self.initial_terrains = NUM_ROWS
        self.score = 0
        self.yshift = 0
        self.player1 = Player(
            (COL_WIDTH * (int(NUM_COLS / 2) + 0.5)), (NUM_ROWS * (ROW_HEIGHT)) - ROW_HEIGHT / 2)
        self.create_board()
        self.highscore = 0
        self.set_high_score()
        self.bg_music = bgmusic # source: https://freesound.org/people/Sunsai/sounds/415804/
        self.bg_music.loop()

    def create_board(self):
        # first lane should be empty grass
        first_lane = Terrain(GAME_HEIGHT - ROW_HEIGHT, "grass")
        # since lane is initialised with obstacles by default, we remove all
        # objects...
        while len(first_lane) > 0:
            first_lane.pop()
        self.terrain_list.append(first_lane)
        counter = 2  # starting from the bottom of the screen...
        for terrain in range(self.initial_terrains - 1):
            # making sure water does not occur twice in a row
            if self.terrain_list[-1].type == "water":
                self.create_terrain(GAME_HEIGHT - (counter * ROW_HEIGHT), terrain_types_nowater[random.randint(0, len(terrain_types_nowater)-1)])
            else:
                self.create_terrain(GAME_HEIGHT - (counter * ROW_HEIGHT),terrain_types[random.randint(0, len(terrain_types) - 1)])
            counter += 1

    def create_terrain(self, y, type):
        exclude_list = []
        for obstacle in self.terrain_list[-1]:
            if obstacle.vx == 0:  # checking for static object in previous lane
                exclude_list.append(obstacle.x // COL_WIDTH)
        if self.terrain_list[-1].type == "road" and type == "water": # making sure that lilypads do not appear on the far left of the screen
            for i in range(0, NUM_ROWS // 2):
                exclude_list.append(i)
        if len(self.terrain_list) > 2: #eliminating the possibility that two rivers would bound a 1-2 lanes of grass with blocking bushes 
            if self.terrain_list[-2].type == "water" and type == "water":
                for i in range(0,NUM_ROWS-1):
                    if i != self.terrain_list[-2][0].x // COL_WIDTH:
                        exclude_list.append(i)
        if len(self.terrain_list) > 3:
            if self.terrain_list[-3].type == "water" and type == "water":
                for i in range(0,NUM_ROWS-1):
                    if i != self.terrain_list[-3][0].x // COL_WIDTH:
                        exclude_list.append(i)
        temp = Terrain(y, type, exclude_list)
        self.terrain_list.append(temp)

    def remove_last_terrain(self, index):
        del self.terrain_list[index]

    def collision_check(self):
        for terrain in self.terrain_list:
            if terrain.type == "road":
                for car in terrain:
                    if car.x <= self.player1.x and car.y <= self.player1.y <= car.y + car.h and car.x + car.l >= self.player1.x - self.player1.r + self.player1.buffer:
                        # checking player on the right
                        # print("Collision")
                        game.state = False
                    elif car.x >= self.player1.x and car.y <= self.player1.y <= car.y + car.h and car.x <= self.player1.x + self.player1.r - self.player1.buffer:
                        # print("Collision")
                        game.state = False
            elif terrain.type == "water":
                if terrain.x <= self.player1.x <= terrain.x + GAME_WIDTH and terrain.y <= self.player1.y <= terrain.y + ROW_HEIGHT:
                    for lilypad in terrain:
                        if lilypad.check_collision_circles(self.player1):
                            continue
                        else:
                            # print("Drown")
                            game.state = False
            elif terrain.type == "grass":
                for obstacle in terrain:
                    if obstacle.check_collision_circles(self.player1) and obstacle.vx > 0:
                        # print("Stung")
                        game.state = False

    def reset(self):
        self.state = True  # is the game active
        # list of terrain objects, last object is the highest in the board
        self.terrain_list = []
        self.initial_terrains = NUM_ROWS
        self.score = 0
        self.yshift = 0
        self.player1 = Player((COL_WIDTH * (int(NUM_COLS / 2) + 0.5)), (NUM_ROWS * (ROW_HEIGHT)) - ROW_HEIGHT / 2)
        self.create_board()
    
    def set_high_score(self):
        for score in high_score:
            if int(score) > self.highscore:
                self.highscore = int(score)

    def display(self):
        for terrain in self.terrain_list:
            terrain.display()
        self.player1.display()
        self.collision_check()
        
        if game.state == False:
            fill(1,100)
            rect(0, 0, GAME_WIDTH, GAME_HEIGHT)
            fill(255)
            textSize(32)
            text("Game over!\nYour score is " + str(self.score) + ".\n"+"High Score: " + str(self.highscore) + "\nClick to restart.", 3 * COL_WIDTH, ROW_HEIGHT * 4)
            if str(self.score) not in high_score:
                high_score.append(str(self.score))
                saveStrings("high_scores.txt",high_score)
                self.set_high_score()
            
# Making it inherit from a list instead of trying to change the obstacles
# list attribute inside
class Terrain(list):

    def __init__(self, y, type, exclude_list=[]):
        self.type = type  # choosing one terrain from terrain_types
        self.speed = 5  # base speed of objects in terrain
        self.x = 0  # always 0, x-coordinate on left of screen)
        self.y = y
        self.num_obs = random.randint(1, 2)
        self.obstacles_location = []
        self.r = 40
        self.exclude_list = exclude_list
        # obs initialises the obstacles, shifted it here so it only does that
        # once at the start
        self.obs()
        self.img = None
        self.setimg()

    # initialises the obstacles, made a lot of changes here to limit edge cases
    def obs(self):
        if self.type == "road":
            for i in range(self.num_obs):
                self.speed = 3
                location = random.randint(1, NUM_COLS - 2)
                # making sure cars dont overlap
                while location in self.obstacles_location:
                    location = random.randint(1, NUM_COLS - 2)

                self.obstacles_location.append(location)
                self.obstacles_location.append(location + 1)
                # next 2 spots blocked out
                self.obstacles_location.append(location - 1)

                # true location is in multiples of 3
                loc = COL_WIDTH * (self.obstacles_location[i * (3)])
                temp = Car(loc, self.y + ROW_HEIGHT * 0.1, self.speed, "car")
                self.append(temp)

        if self.type == "water":
            for i in range(1):
                self.speed = 0
                # prevents lily pads from generating at the edge of board
                location = random.randint(1, NUM_COLS - 2)
                while location in self.obstacles_location or location in self.exclude_list:
                    # prevents blocking of lily pads
                    location = random.randint(1, NUM_COLS - 2)
                self.obstacles_location.append(location)
                loc = COL_WIDTH * (self.obstacles_location[i] + 0.5)
                temp = Obstacle(
                    loc, self.y + self.r, self.r, self.speed, self.type, "lilypad")
                self.append(temp)

        if self.type == "grass":
            for i in range(self.num_obs):
                self.speed = random.randint(0, 6)
                if self.speed < 5:
                    self.speed = 0
                location = random.randint(1, NUM_COLS - 2)
                while location in self.obstacles_location or location in self.exclude_list:
                    location = random.randint(1, NUM_COLS - 2)
                self.obstacles_location.append(location)
                loc = COL_WIDTH * (self.obstacles_location[i] + 0.5)
                if self.speed > 0:
                    temp = Obstacle(
                        loc, self.y + self.r, self.r, self.speed, self.type, "bee")
                if self.speed == 0:
                    temp = Obstacle(
                        loc, self.y + self.r, self.r, self.speed, self.type, "bush")
                self.append(temp)

    def update(self):
        for obstacle in self:
            if obstacle.typ == 'road':
                if obstacle.x > GAME_WIDTH:
                    obstacle.x = 0 - COL_WIDTH * 1.5
            elif obstacle.typ == 'grass':
                if obstacle.dir == RIGHT and obstacle.x + obstacle.r >= GAME_WIDTH:
                    obstacle.dir = LEFT
                if obstacle.dir == LEFT and obstacle.x - obstacle.r < 0:
                    obstacle.dir = RIGHT

            if self.type == 'grass':
                # checking if there is more than one object in the terrain
                if len(self) > 1:
                    # checking if there is a static object
                    if obstacle.vx == 0:
                        for moving_object in self:
                            # checking if there is a moving object
                            if moving_object.vx > 0:
                                if moving_object.check_collision_circles(obstacle) == True:
                                    if moving_object.dir == RIGHT:
                                        moving_object.dir = LEFT
                                    elif moving_object.dir == LEFT:
                                        moving_object.dir = RIGHT
                                        
    def setimg(self):
        if self.type == "grass":
            self.img = grass_images[random.randint(0,2)]
        if self.type == "road":
            self.img = road_images[random.randint(0,2)]    
        if self.type == "water":
            self.img = water_images[random.randint(0,2)]
            
    def display(self):
        self.update()
        noStroke()
        if self.type == "road":
            image(self.img, self.x, self.y + game.yshift,
                  NUM_COLS * COL_WIDTH, ROW_HEIGHT)
        if self.type == "water":
            image(self.img, self.x, self.y + game.yshift,
                  NUM_COLS * COL_WIDTH, ROW_HEIGHT)
        if self.type == "grass":
            image(self.img, self.x, self.y + game.yshift,
                  NUM_COLS * COL_WIDTH, ROW_HEIGHT)
        for i in self:
            i.display()

class Obstacle:  # non-car

    def __init__(self, x, y, r, vx, typ, kind):
        self.x = x
        self.y = y
        self.r = r
        self.vx = vx
        self.dir = RIGHT
        self.typ = typ  # the type of terrain it is on
        self.kind = kind  # the type of obstacle it is
        self.img = None
        self.setimg()

    def update(self):
        if self.dir == RIGHT:
            self.x = self.x + self.vx
        if self.dir == LEFT:
            self.x = self.x - self.vx
    
    def setimg(self):
        if self.kind == "bee":
            self.img = bee_image
        elif self.kind == "lilypad":
            self.img = lilypad_images[random.randint(0,2)]
        else:
            self.img = bush_images[random.randint(0,2)]
            
    def display(self):
        self.update()
        if self.dir == RIGHT:
            image(self.img, self.x - COL_WIDTH / 2, self.y + game.yshift -
                  ROW_HEIGHT / 2, COL_WIDTH, ROW_HEIGHT, 0, 0, COL_WIDTH, ROW_HEIGHT)
        if self.dir == LEFT:
            image(self.img, self.x - COL_WIDTH / 2, self.y + game.yshift -
                  ROW_HEIGHT / 2, COL_WIDTH, ROW_HEIGHT, COL_WIDTH, 0, 0, ROW_HEIGHT)

    def check_collision_circles(self, target):
        if ((self.x - target.x) ** 2 + (self.y - target.y) ** 2) ** 0.5 < self.r + target.r:
            return True
        else:
            return False

    def check_touch_circles(self, target):
        if self.x + self.r + target.r == target.x or self.y + self.r + target.r == target.y:
            return True
        else:
            return False

class Car:

    def __init__(self, x, y, vx, kind):
        self.x = x
        self.y = y
        self.l = COL_WIDTH * 1.5
        self.h = ROW_HEIGHT * 0.8
        self.vx = vx
        self.dir = RIGHT
        self.typ = "road"
        self.kind = kind
        self.img = car_images[random.randint(0,2)]

    def update(self):
        if self.dir == RIGHT:
            self.x = self.x + self.vx
        if self.dir == LEFT:
            self.x = self.x - self.vx

    def display(self):
        self.update()
        image(self.img, self.x, self.y + game.yshift, self.l, self.h)

class Player:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 40
        self.direction="FRONT"
        # will begin at 0, the 0th terrain in game.terrain_list
        self.terrain_number = NUM_ROWS - (self.y) // 80 - 1
        self.buffer = 10  # 10 pixel buffer for car collisions
        self.firstpoint = False #to check if the first point has been given
        self.bounce = bounce # source: https://freesound.org/people/Leszek_Szary/sounds/146726/
        self.img = butterfly_images[butterfly_directions.index("f")]

    def display(self):
        if self.direction == "RIGHT":
            self.img = butterfly_images[butterfly_directions.index("r")]
            image(self.img, self.x - COL_WIDTH / 2, self.y + game.yshift - ROW_HEIGHT / 2, COL_WIDTH, ROW_HEIGHT, 0, 0, COL_WIDTH, ROW_HEIGHT)
        if self.direction == "LEFT":
            self.img = butterfly_images[butterfly_directions.index("l")]
            image(self.img, self.x - COL_WIDTH / 2, self.y + game.yshift - ROW_HEIGHT / 2, COL_WIDTH, ROW_HEIGHT, 0, 0, COL_WIDTH, ROW_HEIGHT)
        if self.direction == "FRONT":
            self.img = butterfly_images[butterfly_directions.index("f")]
            image(self.img, self.x - COL_WIDTH / 2, self.y + game.yshift - ROW_HEIGHT / 2, COL_WIDTH, ROW_HEIGHT, 0, 0, COL_WIDTH, ROW_HEIGHT)
        if self.direction == "BACK":
            self.img = butterfly_images[butterfly_directions.index("b")]
            image(self.img, self.x - COL_WIDTH / 2, self.y + game.yshift - ROW_HEIGHT / 2, COL_WIDTH, ROW_HEIGHT, COL_WIDTH, 0, 0, ROW_HEIGHT)

    def move_left(self):
        if self.x - COL_WIDTH > 0 and self.check_movement(self.x - COL_WIDTH, self.y, 0) and game.state == True:
            self.direction="LEFT"
            self.bounce.rewind()
            self.bounce.play()
            self.x = self.x - COL_WIDTH

    def move_right(self):
        if self.x + COL_WIDTH < COL_WIDTH * NUM_COLS and self.check_movement(self.x + COL_WIDTH, self.y, 0) and game.state == True:
            self.direction = "RIGHT"
            self.bounce.rewind()
            self.bounce.play()
            self.x = self.x + COL_WIDTH

    def move_up(self):
        if self.check_movement(self.x, self.y - ROW_HEIGHT, 1) and game.state == True:
            self.bounce.rewind()
            self.bounce.play()
            self.direction="FRONT"
            self.y = self.y - ROW_HEIGHT  # moving player forward at start
            if self.terrain_number == 0 and self.y == GAME_HEIGHT - 1.5*ROW_HEIGHT and self.firstpoint == False: #only adds a point if player is moving from row 0 to row 1.
                game.score += 1
                self.firstpoint = True
        # when the player moves from the second row forward and shifts board
        if self.y + game.yshift < GAME_HEIGHT - 2 * ROW_HEIGHT:
            game.yshift += 80
            game.score += 1
            if game.terrain_list[-1].type == "water":
                # making sure water doesn't generate twice
                game.create_terrain(game.terrain_list[-1].y - COL_WIDTH, "road")
            else:
                game.create_terrain(game.terrain_list[-1].y - COL_WIDTH, terrain_types[random.randint(0, len(terrain_types) - 1)])  # generates a random terrain
            game.remove_last_terrain(0)
        self.terrain_number = NUM_ROWS - (self.y + game.yshift) // 80 - 1

    def move_down(self):
        self.direction="BACK"
        # checking for boundaries,
        if self.y + game.yshift < GAME_HEIGHT - ROW_HEIGHT and self.check_movement(self.x, self.y + ROW_HEIGHT, -1) and game.state == True:
            self.bounce.rewind()
            self.bounce.play()
            self.y = self.y + ROW_HEIGHT
        # terrain number is used under check_movement to see if movement is
        # blocked
        self.terrain_number = NUM_ROWS - (self.y + game.yshift) // 80 - 1

    # vertical_movement can be filled with +1 or -1
    def check_movement(self, new_x, new_y, vertical_movement):
        for obstacle in game.terrain_list[self.terrain_number + vertical_movement]:
            if game.terrain_list[self.terrain_number + vertical_movement].type == "grass" and obstacle.vx == 0 and obstacle.x == new_x and obstacle.y == new_y:
                return False
        return True

game = Gameboard()

def keyPressed():
    if keyCode == LEFT:
        game.player1.move_left()
    elif keyCode == RIGHT:
        game.player1.move_right()
    elif keyCode == UP:
        game.player1.move_up()
    elif keyCode == DOWN:
        game.player1.move_down()

def mousePressed():
    if not game.state:
        game.reset()

def setup():
    size(GAME_WIDTH, GAME_HEIGHT)
    background(210)

def draw():
    game.display()
    textSize(30)
    fill(37, 72, 156)
    text("Score: " + str(game.score), 7 * COL_WIDTH, ROW_HEIGHT / 3)
    
