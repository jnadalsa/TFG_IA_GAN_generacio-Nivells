'''
=============================
Dungeon Generation Algorithms
=============================

This is an implimentation of some of the dungeon generating
algorithms that are often brought up when talking about roguelikes.

Most of these algorithms have been copied from online sources.
I've included those sources where aplicable.

A lot of my implimentations of these algorithms are overly complicated
(especially in how the different algorithm classes interact with
the rest of the module). The main reason for this is that I wanted
each of the algorithm classes to be easily portable into other
projects. My success in that reguard is up for debate.
'''
import os

import tcod
import random
import time
from math import sqrt
from collections import OrderedDict
from tcod import libtcodpy

SCREEN_WIDTH = 30
SCREEN_HEIGHT = 30
TEXTBOX_HEIGHT = 10
count = 12101

MAP_WIDTH = SCREEN_WIDTH
#MAP_HEIGHT = SCREEN_HEIGHT - TEXTBOX_HEIGHT
MAP_HEIGHT = SCREEN_HEIGHT
USE_PREFABS = False


# ==== Display Class ====

class UserInterface:
    def __init__(self):
        tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
        tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Roguelike Dungeon Comparison',
                               False)  # TODO: Change Game Name
        self.con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

        # self.textBox = tcod.console_new(SCREEN_WIDTH, TEXTBOX_HEIGHT)
        # self.helpText = OrderedDict([
        #     ("1", "Cellular Automata"),
        #     ("2", "Generate rooms"),
        #     ("3", "Save room"),
        #     ("0", "Change Color Scheme"),
        #     ("Space", "Remake Dungeon")
        # ])

        self._colorScheme = 0
        self.setColorScheme(self._colorScheme)

        global keyboard

        keyboard = tcod.Key()

        self.map = Map()
        self.map.generateLevel(MAP_WIDTH, MAP_HEIGHT)

    def mainLoop(self):

        while not tcod.console_is_window_closed():
            global keyboard

            # Input
            keyboard = tcod.console_check_for_keypress()
            exit = self.handleInput(keyboard)
            if (exit): break

            # Render
            self.renderAll()

            tcod.console_flush()

    def handleInput(self, keyboard):
        global count
        if (keyboard.vk == tcod.KEY_ESCAPE):
            return True  # Exit Program

        if (keyboard.vk == tcod.KEY_SPACE):
            # Generate a level based on the last generator used
            self.map.level = self.map._previousGenerator.generateLevel(MAP_WIDTH, MAP_HEIGHT)

        if (keyboard.vk == tcod.KEY_0):
            # cycle through color schemes
            self._colorScheme = (self._colorScheme + 1) % len(ColorScheme._scheme)
            self.setColorScheme(self._colorScheme)

        if (keyboard.vk == tcod.KEY_1):
            # generate map with cellular automata
            self.map.useCellularAutomata()

        if (keyboard.vk == tcod.KEY_2):
            # generate map with room adition
            self.map.useRoomAddition()


        if (keyboard.vk == tcod.KEY_3):
            # save image

            tcod.console.save_xp("maps/map%03i.xp" % count, [self.con])
            count += 1

        if (keyboard.vk == tcod.KEY_4):
            for i in range(100000):
                self.map.useCellularAutomata()
                self.renderAll()
                tcod.console.save_xp("maps/map%03i.xp" % count, [self.con])
                count += 1


        if (keyboard.vk == tcod.KEY_7):
            # generate map with maze with rooms algorithm
            self.map.useMazeWithRooms()

        if (keyboard.vk == tcod.KEY_8):
            # generate map with messy bsp tree
            self.map.useMessyBSPTree()

    def renderAll(self):
        # ==== Render Level ====
        # changed MAP_HEIGHT
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.map.level[x][y] == 1:
                    tcod.console_put_char_ex(self.con, x, y, '#', self.color_light_wall_fore,
                                             self.color_light_wall_back)
                else:
                    tcod.console_put_char_ex(self.con, x, y, '.', self.color_light_ground_fore,
                                             self.color_light_ground_back)

        # TODO: Print Instructions to Screen
        #self.renderTextBox()


        # ==== Blit Console to Screen ====
        tcod.console_blit(self.con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)


    def renderTextBox(self):
        tcod.console_set_default_background(self.textBox, tcod.black)
        tcod.console_set_default_foreground(self.textBox, tcod.white)
        tcod.console_clear(self.textBox)

        keys = self.helpText.keys()
        x = 2
        y = 1
        for key in keys:

            tcod.console_print_ex(self.textBox, x, y, tcod.BKGND_NONE, tcod.LEFT,
                                  key + ") " + self.helpText[key])

            if 0 < (y + 2) < TEXTBOX_HEIGHT - 1:
                y += 2
            else:
                x += 26
                y = 1

        tcod.console_blit(self.textBox, 0, 0, SCREEN_WIDTH, TEXTBOX_HEIGHT, 0, 0, SCREEN_HEIGHT - TEXTBOX_HEIGHT)

    def setColorScheme(self, colorScheme):
        self.color_light_wall_fore = ColorScheme._scheme[colorScheme][0]
        self.color_light_wall_back = ColorScheme._scheme[colorScheme][1]
        self.color_light_ground_fore = ColorScheme._scheme[colorScheme][2]
        self.color_light_ground_back = ColorScheme._scheme[colorScheme][3]


class ColorScheme():
    _scheme = []

    # DEFAULT
    BLUE = [
        tcod.Color(100, 100, 100),  # color_light_wall_fore
        tcod.Color(50, 50, 150),  # color_light_wall_back
        tcod.gray,  # color_light_ground_fore
        tcod.Color(10, 10, 10)  # color_light_ground_back
    ]
    _scheme.append(BLUE)

    MAUVE = [
        tcod.Color(50, 50, 50),  # color_light_wall_fore
        tcod.Color(204, 153, 255),  # color_light_wall_back
        tcod.gray,  # color_light_ground_fore
        tcod.Color(10, 10, 10)  # color_light_ground_back
    ]
    _scheme.append(MAUVE)

    GRAYSCALE = [
        tcod.black,  # color_light_wall_fore
        tcod.gray,  # color_light_wall_back
        tcod.white,  # color_light_ground_fore
        tcod.black  # color_light_ground_back
    ]
    _scheme.append(GRAYSCALE)

    TEXTONLY = [
        tcod.white,  # color_light_wall_fore
        tcod.black,  # color_light_wall_back
        tcod.white,  # color_light_ground_fore
        tcod.black  # color_light_ground_back
    ]
    _scheme.append(TEXTONLY)


# ==== Map Class ====

class Map:
    def __init__(self):
        self.level = []
        '''
		level values of 1 are walls
		level values of 0 are floors
		'''
        self._previousGenerator = self

        self.cellularAutomata = CellularAutomata()




    def generateLevel(self, MAP_WIDTH, MAP_HEIGHT):
        # Creates an empty 2D array or clears existing array
        self.level = [[0
                       for y in range(MAP_HEIGHT)]
                      for x in range(MAP_WIDTH)]

        return self.level

        print("Flag: map.generateLevel()")



    def useCellularAutomata(self):
        self.level = self.cellularAutomata.generateLevel(MAP_WIDTH, MAP_HEIGHT)
        self._previousGenerator = self.cellularAutomata




# ==== Cellular Automata ====
class CellularAutomata:
    '''
	Rather than implement a traditional cellular automata, I
	decided to try my hand at a method discribed by "Evil
	Scientist" Andy Stobirski that I recently learned about
	on the Grid Sage Games blog.
	'''

    def __init__(self):
        self.level = []

        self.iterations = 30000
        self.neighbors = 4  # number of neighboring walls for this cell to become a wall
        self.wallProbability = 0.50  # the initial probability of a cell becoming a wall, recommended to be between .35 and .55

        self.ROOM_MIN_SIZE = 16  # size in total number of cells, not dimensions
        self.ROOM_MAX_SIZE = 500  # size in total number of cells, not dimensions

        self.smoothEdges = True
        self.smoothing = 1

    def generateLevel(self, mapWidth, mapHeight):
        # Creates an empty 2D array or clears existing array
        self.caves = []

        self.level = [[1
                       for y in range(mapHeight)]
                      for x in range(mapWidth)]

        self.randomFillMap(mapWidth, mapHeight)

        self.createCaves(mapWidth, mapHeight)

        self.getCaves(mapWidth, mapHeight)

        self.connectCaves(mapWidth, mapHeight)

        self.cleanUpMap(mapWidth, mapHeight)
        return self.level

    def randomFillMap(self, mapWidth, mapHeight):
        for y in range(1, mapHeight - 1):
            for x in range(1, mapWidth - 1):
                # print("(",x,y,") = ",self.level[x][y])
                if random.random() >= self.wallProbability:
                    self.level[x][y] = 0

    def createCaves(self, mapWidth, mapHeight):
        # ==== Create distinct caves ====
        for i in range(0, self.iterations):
            # Pick a random point with a buffer around the edges of the map
            tileX = random.randint(1, mapWidth - 2)  # (2,mapWidth-3)
            tileY = random.randint(1, mapHeight - 2)  # (2,mapHeight-3)

            # if the cell's neighboring walls > self.neighbors, set it to 1
            if self.getAdjacentWalls(tileX, tileY) > self.neighbors:
                self.level[tileX][tileY] = 1
            # or set it to 0
            elif self.getAdjacentWalls(tileX, tileY) < self.neighbors:
                self.level[tileX][tileY] = 0

        # ==== Clean Up Map ====
        self.cleanUpMap(mapWidth, mapHeight)

    def cleanUpMap(self, mapWidth, mapHeight):
        if (self.smoothEdges):
            for i in range(0, 5):
                # Look at each cell individually and check for smoothness
                for x in range(1, mapWidth - 1):
                    for y in range(1, mapHeight - 1):
                        if (self.level[x][y] == 1) and (self.getAdjacentWallsSimple(x, y) <= self.smoothing):
                            self.level[x][y] = 0

    def createTunnel(self, point1, point2, currentCave, mapWidth, mapHeight):
        # run a heavily weighted random Walk
        # from point1 to point1
        drunkardX = point2[0]
        drunkardY = point2[1]
        while (drunkardX, drunkardY) not in currentCave:
            # ==== Choose Direction ====
            north = 1.0
            south = 1.0
            east = 1.0
            west = 1.0

            weight = 1

            # weight the random walk against edges
            if drunkardX < point1[0]:  # drunkard is left of point1
                east += weight
            elif drunkardX > point1[0]:  # drunkard is right of point1
                west += weight
            if drunkardY < point1[1]:  # drunkard is above point1
                south += weight
            elif drunkardY > point1[1]:  # drunkard is below point1
                north += weight

            # normalize probabilities so they form a range from 0 to 1
            total = north + south + east + west
            north /= total
            south /= total
            east /= total
            west /= total

            # choose the direction
            choice = random.random()
            if 0 <= choice < north:
                dx = 0
                dy = -1
            elif north <= choice < (north + south):
                dx = 0
                dy = 1
            elif (north + south) <= choice < (north + south + east):
                dx = 1
                dy = 0
            else:
                dx = -1
                dy = 0

            # ==== Walk ====
            # check colision at edges
            if (0 < drunkardX + dx < mapWidth - 1) and (0 < drunkardY + dy < mapHeight - 1):
                drunkardX += dx
                drunkardY += dy
                if self.level[drunkardX][drunkardY] == 1:
                    self.level[drunkardX][drunkardY] = 0

    def getAdjacentWallsSimple(self, x, y):  # finds the walls in four directions
        wallCounter = 0
        # print("(",x,",",y,") = ",self.level[x][y])
        if (self.level[x][y - 1] == 1):  # Check north
            wallCounter += 1
        if (self.level[x][y + 1] == 1):  # Check south
            wallCounter += 1
        if (self.level[x - 1][y] == 1):  # Check west
            wallCounter += 1
        if (self.level[x + 1][y] == 1):  # Check east
            wallCounter += 1

        return wallCounter

    def getAdjacentWalls(self, tileX, tileY):  # finds the walls in 8 directions
        pass
        wallCounter = 0
        for x in range(tileX - 1, tileX + 2):
            for y in range(tileY - 1, tileY + 2):
                if (self.level[x][y] == 1):
                    if (x != tileX) or (y != tileY):  # exclude (tileX,tileY)
                        wallCounter += 1
        return wallCounter

    def getCaves(self, mapWidth, mapHeight):
        # locate all the caves within self.level and stor them in self.caves
        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                if self.level[x][y] == 0:
                    self.floodFill(x, y)

        for set in self.caves:
            for tile in set:
                self.level[tile[0]][tile[1]] = 0

        # check for 2 that weren't changed.
        '''
		The following bit of code doesn't do anything. I 
		put this in to help find mistakes in an earlier 
		version of the algorithm. Still, I don't really 
		want to remove it.
		'''
        for x in range(0, mapWidth):
            for y in range(0, mapHeight):
                if self.level[x][y] == 2:
                    print("(", x, ",", y, ")")

    def floodFill(self, x, y):
        '''
		flood fill the separate regions of the level, discard
		the regions that are smaller than a minimum size, and
		create a reference for the rest.
		'''
        cave = set()
        tile = (x, y)
        toBeFilled = set([tile])
        while toBeFilled:
            tile = toBeFilled.pop()

            if tile not in cave:
                cave.add(tile)

                self.level[tile[0]][tile[1]] = 1

                # check adjacent cells
                x = tile[0]
                y = tile[1]
                north = (x, y - 1)
                south = (x, y + 1)
                east = (x + 1, y)
                west = (x - 1, y)

                for direction in [north, south, east, west]:

                    if self.level[direction[0]][direction[1]] == 0:
                        if direction not in toBeFilled and direction not in cave:
                            toBeFilled.add(direction)

        if len(cave) >= self.ROOM_MIN_SIZE:
            self.caves.append(cave)

    def connectCaves(self, mapWidth, mapHeight):
        # Find the closest cave to the current cave
        for currentCave in self.caves:
            for point1 in currentCave: break  # get an element from cave1
            point2 = None
            distance = 0
            for nextCave in self.caves:
                if nextCave != currentCave and not self.checkConnectivity(currentCave, nextCave):
                    # choose a random point from nextCave
                    for nextPoint in nextCave: break  # get an element from cave1
                    # compare distance of point1 to old and new point2
                    newDistance = self.distanceFormula(point1, nextPoint)
                    if (newDistance < distance) or distance == 0:
                        point2 = nextPoint
                        distance = newDistance

            if point2:  # if all tunnels are connected, point2 == None
                self.createTunnel(point1, point2, currentCave, mapWidth, mapHeight)

    def distanceFormula(self, point1, point2):
        d = sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
        return d

    def checkConnectivity(self, cave1, cave2):
        # floods cave1, then checks a point in cave2 for the flood

        connectedRegion = set()
        for start in cave1: break  # get an element from cave1

        toBeFilled = set([start])
        while toBeFilled:
            tile = toBeFilled.pop()

            if tile not in connectedRegion:
                connectedRegion.add(tile)

                # check adjacent cells
                x = tile[0]
                y = tile[1]
                north = (x, y - 1)
                south = (x, y + 1)
                east = (x + 1, y)
                west = (x - 1, y)

                for direction in [north, south, east, west]:

                    if self.level[direction[0]][direction[1]] == 0:
                        if direction not in toBeFilled and direction not in connectedRegion:
                            toBeFilled.add(direction)

        for end in cave2: break  # get an element from cave2

        if end in connectedRegion:
            return True

        else:
            return False




# ==== TinyKeep ====
'''
https://www.reddit.com/r/gamedev/comments/1dlwc4/procedural_dungeon_generation_algorithm_explained/
and
http://www.gamasutra.com/blogs/AAdonaac/20150903/252889/Procedural_Dungeon_Generation_Algorithm.php
'''


# ==== Helper Classes ====
class Rect:  # used for the tunneling algorithm
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        centerX = int((self.x1 + self.x2) / 2)
        centerY = int((self.y1 + self.y2) / 2)
        return (centerX, centerY)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Leaf:  # used for the BSP tree algorithm
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.MIN_LEAF_SIZE = 10
        self.child_1 = None
        self.child_2 = None
        self.room = None
        self.hall = None

    def splitLeaf(self):
        # begin splitting the leaf into two children
        if (self.child_1 != None) or (self.child_2 != None):
            return False  # This leaf has already been split

        '''
		==== Determine the direction of the split ====
		If the width of the leaf is >25% larger than the height,
		split the leaf vertically.
		If the height of the leaf is >25 larger than the width,
		split the leaf horizontally.
		Otherwise, choose the direction at random.
		'''
        splitHorizontally = random.choice([True, False])
        if (self.width / self.height >= 1.25):
            splitHorizontally = False
        elif (self.height / self.width >= 1.25):
            splitHorizontally = True

        if (splitHorizontally):
            max = self.height - self.MIN_LEAF_SIZE
        else:
            max = self.width - self.MIN_LEAF_SIZE

        if (max <= self.MIN_LEAF_SIZE):
            return False  # the leaf is too small to split further

        split = random.randint(self.MIN_LEAF_SIZE, max)  # determine where to split the leaf

        if (splitHorizontally):
            self.child_1 = Leaf(self.x, self.y, self.width, split)
            self.child_2 = Leaf(self.x, self.y + split, self.width, self.height - split)
        else:
            self.child_1 = Leaf(self.x, self.y, split, self.height)
            self.child_2 = Leaf(self.x + split, self.y, self.width - split, self.height)

        return True

    def createRooms(self, bspTree):
        if (self.child_1) or (self.child_2):
            # recursively search for children until you hit the end of the branch
            if (self.child_1):
                self.child_1.createRooms(bspTree)
            if (self.child_2):
                self.child_2.createRooms(bspTree)

            if (self.child_1 and self.child_2):
                bspTree.createHall(self.child_1.getRoom(),
                                   self.child_2.getRoom())

        else:
            # Create rooms in the end branches of the bsp tree
            w = random.randint(bspTree.ROOM_MIN_SIZE, min(bspTree.ROOM_MAX_SIZE, self.width - 1))
            h = random.randint(bspTree.ROOM_MIN_SIZE, min(bspTree.ROOM_MAX_SIZE, self.height - 1))
            x = random.randint(self.x, self.x + (self.width - 1) - w)
            y = random.randint(self.y, self.y + (self.height - 1) - h)
            self.room = Rect(x, y, w, h)
            bspTree.createRoom(self.room)

    def getRoom(self):
        if (self.room):
            return self.room

        else:
            if (self.child_1):
                self.room_1 = self.child_1.getRoom()
            if (self.child_2):
                self.room_2 = self.child_2.getRoom()

            if (not self.child_1 and not self.child_2):
                # neither room_1 nor room_2
                return None

            elif (not self.room_2):
                # room_1 and !room_2
                return self.room_1

            elif (not self.room_1):
                # room_2 and !room_1
                return self.room_2

            # If both room_1 and room_2 exist, pick one
            elif (random.random() < 0.5):
                return self.room_1
            else:
                return self.room_2


class Prefab(Rect):
    pass


if __name__ == "__main__":
    ui = UserInterface()
    ui.mainLoop()
