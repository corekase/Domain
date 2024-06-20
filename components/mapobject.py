import pygame
from queue import Queue
from math import cos, sin, atan2, radians, degrees, sqrt
from .utility import tile_graphical_centre
from collections import namedtuple
from pygame.sprite import Sprite
from random import randint

# commands and their parameters for the command queue
Stall = namedtuple('Stall', 'none')
Move_To = namedtuple('Move_To', 'destination')
Path_To = namedtuple('Path_To', 'position')

class MapObject(Sprite):
    # reference for the map object
    map = None
    # tile gid's for wall and floor in tilesheet
    FLOOR, WALL = 1, 2

    def __init__(self):
        super().__init__()
        # values that must be filled in by subclasses in their init and before any calls to process()
        self.normal_image = None
        self.overlap_image = None
        self.image = None
        self.rect = None
        self.centre_xpos, self.centre_ypos = None, None
        # these values will be updated by rect_sync
        self.x_coord, self.y_coord = None, None
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
            command_name = self.command_name(command)
            # command evaluations
            if command_name == 'Stall':
                # stall does nothing and doesn't remove itself so it effectively suspends the object
                pass
            elif command_name == 'Move_To':
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
            elif command_name == 'Path_To':
                # from current x_coord and y_coord move to destination in cells coordinates
                # this is so the avatar can have a new position, let the last move to a cell
                # complete, clear the rest of the moves and then this instruction picks up
                # to go to the new destination
                position = command.position
                if self.command_name(self.command_queue[0]) == "Move_To":
                    # finish move to, then add path_to command with same position
                    # so command queue = command queue [:1] + path_to command to position
                    pass
                else:
                    # if there was a move_to it's now done

                    # clear the queue
                    self.command_queue = []

                    # find valid path, if no valid path do nothing

                    # do Path_To positions
            else:
                raise(f'Command: {command_name} not implemented')
        else:
            # no commands in command queue, generate some more
            self.process()

    def process(self):
        # override in subclass
        pass

    def command(self, command):
        # add a command to the command queue
        self.command_queue.append(command)

    def command_name(self, command):
        return type(command).__name__

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
            self.command(Move_To(tile_graphical_centre(MapObject.map, position)))

    def find_path(self, position1, position2):
        # call find nearest with a destination list of one position and return just the path
        return self.find_nearest(position1, [position2[0], position2[1], None])[0]

    def find_nearest(self, start_position, destination_objects):
        # data structure for objects for find_nearest
        destination_list = []
        for item in destination_objects:
            destination_list.append([item.x_coord, item.y_coord, item])
        # breadth-first search
        frontier = Queue()
        frontier.put(start_position)
        came_from = dict()
        came_from[start_position] = None
        found = False
        goal = None
        goal_object = None
        while not frontier.empty():
            current = frontier.get()
            for x, y, object in destination_list:
                if (current[0] == x) and (current[1] == y):
                    found = True
                    goal = current
                    goal_object = object
                    break
            if found:
                break
            neighbours = self.adjacents(current)
            for next in neighbours:
                if next not in came_from:
                    frontier.put(next)
                    came_from[next] = current
        if found:
            path = []
            while goal != start_position:
                path.insert(0, goal)
                goal = came_from[goal]
            return path, goal_object
        else:
            return None, None

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
