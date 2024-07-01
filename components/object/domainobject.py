import sys, pygame
from queue import Queue
from math import cos, sin, atan2, radians, degrees, sqrt
from collections import namedtuple
from pygame.sprite import Sprite

# named indexes for tiles to map the correct gid
EMPTY, FLOOR, WALL = 0, 1, 2

# machine epsilon for distance calculation in move_to
eps = sys.float_info.epsilon

# commands and their parameters for the command queue
Stall = namedtuple('Stall', 'none')
Move_To = namedtuple('Move_To', 'destination')
Path_To = namedtuple('Path_To', 'position')
Datagram = namedtuple('Datagram', 'callback argument')
Teleport = namedtuple('Teleport', 'destination')
Chase = namedtuple('Chase', 'target')
Cool_Down = namedtuple('Cool_Down', 'duration')

class Position:
    def __init__(self, position):
        self.x_coord, self.y_coord = position

class DomainObject(Sprite):
    # reference for the map
    map = None
    # reference for domain objects
    domain = None
    # reference for gui manager
    gui = None
    # reference for the domain manager
    domain_manager = None
    # tile gid tuple
    tiles = None

    def __init__(self):
        super().__init__()
        # values filled in by subclasses
        self.normal_image = None
        self.overlap_image = None
        self.image = None
        # values updated by either sync_position or sync_cell
        self.rect = None
        self.centre_xpos, self.centre_ypos = None, None
        self.x_coord, self.y_coord = None, None
        # speed variable, world pixels per second
        self.speed = 0.0
        # list of mapobjects currently overlapping this one
        self.overlaps = []
        # command queue
        self.command_queue = []
        # subclasess must call either sync_position or sync_cell before they exit their __init__

    def update(self, elapsed_time):
        # filter overlapped mapobjects so that only objects still overlapping are kept
        self.overlaps = [domainobject for domainobject in self.overlaps \
                         if pygame.sprite.collide_rect(self, domainobject)]
        # if this agent isn't overlapping other agents return its image to normal
        if len(self.overlaps) == 0:
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
                if self.find_distance_from_self(destination) <= 1.0 + eps:
                    # arrived at destination
                    teleporters = DomainObject.domain_manager.find_cell_objects((self.x_coord, self.y_coord), DomainObject.domain.objects('teleporters'))
                    avatar = DomainObject.domain.objects('avatar')[0]
                    if len(teleporters) > 0 and (self is avatar):
                        # only teleport the avatar, not other moving domain objects
                        self.sync_cell(teleporters[0].destination)
                        # switch to avatar floor and location
                        self.domain_manager.switch_floor(self.domain_manager.get_floor(avatar.x_coord))
                        self.domain_manager.main_viewport = list(avatar.rect.center)
                    else:
                        self.sync_coordinate(destination)
                    # remove this command item from the queue
                    self.command_queue.pop(0)
                else:
                    # move towards destination
                    self.move(self.find_bearing_angle(destination), elapsed_time)
            elif command_name == 'Path_To':
                # from current x_coord and y_coord move to destination in cells coordinates
                destination = command.position
                # remove this command from the queue
                self.command_queue.pop(0)
                # find valid path, if no valid path do nothing
                path = self.find_path((self.x_coord, self.y_coord), destination)
                if path != None:
                    self.follow_path(path)
            elif command_name == 'Datagram':
                # call a method with an argument parameter.  If you need more than one value
                # then make it a tuple of values
                callback, argument = command.callback, command.argument
                self.command_queue.pop(0)
                # call the datagram callback function with the argument
                callback(argument)
            elif command_name == 'Teleport':
                # this command is so that moveable domain objects are able to build an overall
                # path out of smaller segments.  If an agent wanted to go to a room on a different
                # floor they would pathfind to the teleport, use the teleport, and then pathfind
                # to the room on the other floor.  moving an agent using multiple results from
                # pathfinding, traversing to destinations as segments of those path finds and teleports
                pass
            elif command_name == 'Chase':
                # get the cell coordinate of a target and do a find_nearest to it
                # then do one Move_To, then add Chase again so after the Move_To it comes back
                # to get a new chase coordinate each process update
                pass
            elif command_name == 'Cool_Down':
                # track and wait a number of seconds and then remove the cool_down command from the queue
                pass
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
        # return the name of the tuple which is the command
        return type(command).__name__

    def reset_queue(self):
        # clear the queue except for the first in-progress Move_To
        if len(self.command_queue) > 0:
            current = self.command_queue[0]
            if self.command_name(current) == 'Move_To':
                self.command_queue = [current]
                # return that queue wasn't fully cleared
                return False
        self.command_queue.clear()
        # return queue cleared
        return True

    def move(self, degree, elapsed_time):
        # move in the direction of degree
        degree %= 360
        self.sync_coordinate((self.centre_xpos + (cos(radians(degree)) * self.speed) * elapsed_time,
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

    def tile_graphical_centre(self, location):
        # given a tile x and y coordinate return the graphical x and y center point in map pixels
        x_width, y_height = self.map.tilewidth, self.map.tileheight
        x_centre, y_centre = int(x_width / 2), int(y_height / 2)
        return (location[0] * x_width) + x_centre, (location[1] * y_height) + y_centre

    def follow_path(self, path):
        # translate cell coordinates to world pixel coordinate movements for the overall path
        for position in path:
            # tile_graphical_centre does that for each position in the path
            self.command(Move_To(self.tile_graphical_centre(position)))

    def find_path(self, position1, position2):
        # call find nearest with a destination list of one position and return just the path
        return self.find_nearest(position1, [Position(position2)])[0]

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
            adjacents.append(self.domain_manager.find_cell_gid((x + neighbour[0], y + neighbour[1])))
        # the list indexes map by the neighbour deltas as given in this diagram:
        # 0 1 2
        # 3 4 5
        # 6 7 8
        # clear the current tile so it isn't included in neighbours
        adjacents[4] = None
        # with the layout order, block out invalid orthographic moves due to walls
        if adjacents[1] == self.tiles[WALL]:
            adjacents[0] = None
            adjacents[2] = None
        if adjacents[5] == self.tiles[WALL]:
            adjacents[2] = None
            adjacents[8] = None
        if adjacents[7] == self.tiles[WALL]:
            adjacents[6] = None
            adjacents[8] = None
        if adjacents[3] == self.tiles[WALL]:
            adjacents[0] = None
            adjacents[6] = None
        valid_neighbours = []
        for num, value in enumerate(adjacents):
            if value == self.tiles[FLOOR]:
                valid_neighbours.append((x + neighbours[num][0], y + neighbours[num][1]))
        # return neighbours which are floor tiles as cell positions
        return valid_neighbours

    def sync_coordinate(self, position):
        # update position state in pixels
        self.centre_xpos, self.centre_ypos = position
        self.rect.center = int(self.centre_xpos), int(self.centre_ypos)
        self.x_coord, self.y_coord = int(self.rect.centerx / DomainObject.map.tilewidth), int(self.rect.centery / DomainObject.map.tileheight)

    def sync_cell(self, position):
        # update position state in cells
        self.centre_xpos, self.centre_ypos = self.tile_graphical_centre(position)
        self.rect.center = int(self.centre_xpos), int(self.centre_ypos)
        self.x_coord, self.y_coord = position

    def overlap(self, other_object):
        # other_mapobject is overlapping rects with this mapobject, if it's not already in overlap_mapobjects then add it
        if not (other_object in self.overlaps):
            # set visual sprite to overlap image
            self.image = self.overlap_image
            # remember the agent
            self.overlaps.append(other_object)
