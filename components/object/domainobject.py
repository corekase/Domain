import sys, pygame
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
Teleport = namedtuple('Teleport', 'destination follow')

class Coordinate:
    def __init__(self, position):
        self.x_coord, self.y_coord = position

class DomainObject(Sprite):
    # reference for the map, map is a keyword so this has _object added
    map_object = None
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
        # values updated by either sync_coordinate or sync_cell
        self.rect = None
        self.centre_xpos, self.centre_ypos = None, None
        self.x_coord, self.y_coord = None, None
        # speed variable, world pixels per second
        self.speed = 0.0
        # list of domain objects currently overlapping this one
        self.overlaps = []
        # command queue
        self.command_queue = []
        # subclasess must call either sync_coordinate or sync_cell before they exit their __init__

    def update(self, elapsed_time):
        # filter overlapped domain objects so that only objects still overlapping are kept
        self.overlaps = [domainobject for domainobject in self.overlaps \
                         if pygame.sprite.collide_rect(self, domainobject)]
        # if this domain object isn't overlapping other objects return its image to normal
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
                # move straight line to the destination in renderer map rect pixel coordinates
                destination = command.destination
                # check to see if within 1 pixel of location
                if self.find_distance(destination) <= 1.0 + eps:
                    # arrived at destination
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
                path = DomainObject.domain_manager.find_nearest((self.x_coord, self.y_coord), [Coordinate(destination)])[0]
                if path != None:
                    # replaces a path_to with move_to commands without affecting items in the queue after it
                    for position in path:
                        # convert to renderer map rect pixel coordinates for each position in the path
                        self.command_queue.insert(0, Move_To(self.pixel_centre(position)))
            elif command_name == 'Datagram':
                # call a method with an argument parameter.  If you need more than one value
                # then make it a tuple of values
                callback, argument = command.callback, command.argument
                self.command_queue.pop(0)
                # call the datagram callback function with the argument
                callback(argument)
            elif command_name == 'Teleport':
                # teleport to a new position
                destination, follow = command.destination, command.follow
                self.sync_cell(destination)
                self.command_queue.pop(0)
                # if follow then switch floor and main_viewport as well, done within a single command queue item
                if follow:
                    DomainObject.domain_manager.switch_floor(DomainObject.domain_manager.get_floor(destination[0]))
                    DomainObject.domain_manager.main_viewport = list(self.rect.center)
            else:
                raise Exception(f'Command: {command_name} not implemented')
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

    def find_distance(self, position):
        # find distance between self and position
        return sqrt((abs(self.centre_xpos - position[0]) ** 2) + (abs(self.centre_ypos - position[1]) ** 2))

    def pixel_centre(self, location):
        # given a tile x and y cell coordinate return the graphical x and y center point in renderer map rect pixels
        x_width, y_height = self.map_object.tilewidth, self.map_object.tileheight
        x_centre, y_centre = int(x_width / 2), int(y_height / 2)
        return (location[0] * x_width) + x_centre, (location[1] * y_height) + y_centre

    def sync_coordinate(self, position):
        # update position state in pixels
        self.centre_xpos, self.centre_ypos = position
        self.rect.center = int(self.centre_xpos), int(self.centre_ypos)
        self.x_coord, self.y_coord = int(self.rect.centerx / DomainObject.map_object.tilewidth), int(self.rect.centery / DomainObject.map_object.tileheight)

    def sync_cell(self, position):
        # update position state in cells
        self.centre_xpos, self.centre_ypos = self.pixel_centre(position)
        self.rect.center = int(self.centre_xpos), int(self.centre_ypos)
        self.x_coord, self.y_coord = position

    def overlap(self, other_object):
        # other_mapobject is overlapping rects with this mapobject, if it's not already in overlap_mapobjects then add it
        if not (other_object in self.overlaps):
            # set visual sprite to overlap image
            self.image = self.overlap_image
            # remember the agent
            self.overlaps.append(other_object)
