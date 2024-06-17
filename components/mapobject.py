import pygame, heapq
from math import cos, sin, atan2, radians, degrees, sqrt
from .util import image_resource, tile_graphical_centre
from collections import namedtuple
from pygame.sprite import Sprite
from random import randint

# commands and their parameters for the command queue
Move_To = namedtuple('Move_To', 'destination')
Stall = namedtuple('Stall', 'none')

class MapObject(Sprite):
    # reference for the map object
    map = None
    # tile gid's for wall and floor in tilesheet
    WALL, FLOOR = 1, 2

    def __init__(self):
        super().__init__()
        # values to be filled in by subclasses in their init and before any calls to process()
        self.normal_image = None
        self.overlap_image = None
        self.image = None
        self.rect = None
        self.centre_xpos, self.centre_ypos = None, None
        # speed variable, world pixels per second
        self.speed = 0.0
        # list of agents currently overlapping this one
        self.overlap_agents = []
        # command queue
        self.command_queue = []
        # subclasess must do:

        # self.rect_sync((self.centre_xpos, self.centre_ypos))

        # with valid values before they exit their __init__

    def update(self, elapsed_time):
        # filter overlapped agents so that only agents still overlapping are kept
        self.overlap_agents = [agent for agent in self.overlap_agents if pygame.sprite.collide_rect(self, agent)]
        # if this agent isn't overlapping other agents return its image to normal
        if len(self.overlap_agents) == 0:
            self.image = self.normal_image
        # check the command queue for any commands
        if len(self.command_queue) > 0:
            # there is a command, get it
            command = self.command_queue[0]
            command_name = type(command).__name__.lower()
            # command evaluations
            if command_name == 'move_to':
                # move straight line to the destination world pixel coordinates
                destination = command.destination
                # check to see if within 1 pixel of location
                if self.find_distance_from_self(destination) <= 1.0:
                    # arrived at destination
                    self.rect_sync(destination)
                    # remove this command item from the queue
                    self.command_queue.pop(0)
                else:
                    # move towards destination
                    self.move(self.find_bearing_angle(destination), elapsed_time)
            elif command_name == 'stall':
                # stall does nothing, doesn't remove itself, the agent just sits there until something intervenes
                pass
            else:
                raise(f'Command: {command_name} not implemented')
        else:
            # no commands in command queue, generate some more
            self.process()

    def process(self):
        pass

    def move(self, degree, elapsed_time):
        # move in the direction of degree
        degree %= 360
        self.rect_sync((self.centre_xpos + (cos(radians(degree)) * self.speed) * elapsed_time,
                        self.centre_ypos + (sin(radians(degree)) * self.speed) * elapsed_time))

    def find_bearing_angle(self, position):
        # find bearing angle on position
        return degrees(atan2(position[1] - self.centre_ypos, position[0] - self.centre_xpos)) % 360

    def find_distance(self, position1, position2):
        # find distance between position1 and position2, no specific units
        return sqrt((abs(position1[0] - position2[0]) ** 2) + (abs(position1[1] - position2[1]) ** 2))

    def find_distance_from_self(self, position):
        # find distance to position in world pixel lengths
        return self.find_distance((self.centre_xpos, self.centre_ypos),
                                  (position[0], position[1]))

    def follow_path(self, path):
        # translate cell coordinates to world pixel coordinate movements for the overall path
        for position in path:
            # tile_graphical_centre does that for each position in the path
            self.command_queue.append(Move_To(tile_graphical_centre(MapObject.map, position)))

    def find_path(self, position1, position2):
        # Dijkstra’s Algorithm
        # find a path from position1 to position2 consisting only of floor tiles
        class PriorityQueue:
            # supporting queue class
            def __init__(self):
                self.elements = []
            def empty(self):
                return not self.elements
            def put(self, item, priority):
                heapq.heappush(self.elements, (priority, item))
            def get(self):
                return heapq.heappop(self.elements)[1]
        # setup
        frontier = PriorityQueue()
        frontier.put(position1, 0)
        came_from, cost_so_far = {}, {}
        came_from[position1], cost_so_far[position1] = None, 0
        # if while loop exits without setting found to True then there is no path
        found = False
        # main
        while not frontier.empty():
            current = frontier.get()
            # if current and position2 elements are done by tuple comparisons
            # you will occassionally get key errors with position2.  comparing
            # the elements separately solves that problem as follows
            if (current[0] == position2[0]) and (current[1] == position2[1]):
                found = True
                break
            neighbours = self.adjacents(current)
            for next in neighbours:
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost
                    frontier.put(next, priority)
                    came_from[next] = current
        if found:
            # build a path in reverse from position2 to position1
            path = []
            while position2 != position1:
                path.insert(0, position2)
                position2 = came_from[position2]
            return path
        else:
            return None

    def adjacents(self, position):
        x, y = position
        # an ordered 9 element list where indexes are mapped to neighbours which are
        # tuples of delta x and y coordinates around a centre point
        neighbours = ((-1, -1), (0, -1), (1, -1),
                      (-1,  0), (0,  0), (1,  0),
                      (-1,  1), (0,  1), (1,  1))
        adjacents = []
        # fill in ordered list with cell positions by adding neighbour deltas to each axis
        for neighbour in neighbours:
            adjacents.append(self.find_cell_gid((x + neighbour[0], y + neighbour[1])))
        # the list indexes map by the neighbour deltas as given in this diagram:
        # 0 1 2
        # 3 4 5
        # 6 7 8
        # with that layout order, block out invalid orthographic moves due to walls
        adjacents[4] = None
        if adjacents[1] == MapObject.WALL:
            adjacents[0] = None
            adjacents[2] = None
        if adjacents[5] == MapObject.WALL:
            adjacents[2] = None
            adjacents[8] = None
        if adjacents[7] == MapObject.WALL:
            adjacents[6] = None
            adjacents[8] = None
        if adjacents[3] == MapObject.WALL:
            adjacents[0] = None
            adjacents[6] = None
        # filter for floor tiles
        valid_neighbours = []
        for num, value in enumerate(adjacents):
            if value == MapObject.FLOOR:
                valid_neighbours.append((x + neighbours[num][0], y + neighbours[num][1]))
        # return neighbours which are floor tiles as cell positions
        return valid_neighbours

    def find_random_position(self, gid):
        # return a random cell position which contains a specific tile gid
        while True:
            x, y = randint(0, MapObject.map.width - 1), randint(0, MapObject.map.height - 1)
            if self.find_cell_gid((x, y)) == gid:
                return x, y

    def find_cell_gid(self, position):
        # get the tile gid for a cell position
        x, y = position
        if x < 0 or y < 0 or x >= MapObject.map.width or y >= MapObject.map.height:
            return None
        return MapObject.map.get_tile_gid(x, y, 0)

    def rect_sync(self, position):
        # update position state, this chains an affect to drawing functions handled by the sprite parent class
        self.centre_xpos, self.centre_ypos = position
        self.rect.center = int(self.centre_xpos), int(self.centre_ypos)
        self.x_coord, self.y_coord = int(self.rect.centerx / MapObject.map.tilewidth), int(self.rect.centery / MapObject.map.tileheight)

    def overlap(self, other_agent):
        # other_agent is overlapping rects with this agent, if it's not already in overlap_agents then add it
        if not (other_agent in self.overlap_agents):
            # set visual sprite to overlap image
            self.image = self.overlap_image
            # remember the agent
            self.overlap_agents.append(other_agent)
