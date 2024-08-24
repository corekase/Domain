# machine epsilon, smallest difference between floats
import sys
eps = sys.float_info.epsilon

# functions used for movement
from math import sqrt, atan2, cos, sin

# bring in class references
from components.bundled.pytmx import TiledMap
from components.object.objectmanager import ObjectManager
from components.gui.guimanager import GuiManager
from components.domain.domainmanager import DomainManager

# tile cutter
from ..utility import cut_tile

# the name of the namedtuple is the name of the command
from collections import namedtuple

# commands and their parameters for the command queue
Stall = namedtuple('Stall', 'none')
Move_To = namedtuple('Move_To', 'destination')
Teleport = namedtuple('Teleport', 'destination')
Path = namedtuple('Path', 'path')

# all domain objects are subclasses of Sprite
from pygame.sprite import Sprite

class DomainObject(Sprite):
    # reference for the map, map is a keyword so this has _object added
    map_object: TiledMap
    # reference for object manager
    object_manager: ObjectManager
    # reference for gui manager
    gui_manager: GuiManager
    # reference for the domain manager
    domain_manager: DomainManager
    # tile_gid tuple, useful for subclasses
    tile_gid = None

    def __init__(self):
        super().__init__()
        # self.image is managed by the domain object class, subclasses give their animations to it
        self.image = None
        # values updated by either sync_coordinate or sync_cell
        self.centre_xpos = self.centre_ypos = None
        self.coord = None
        # filled in by load_tiles
        self.rect = None
        # world pixels per second
        self.speed = 0.0
        # command queue
        self.command_queue = []
        # list of animation image frames
        self.animations = []
        # internal timer for animation frames
        self.timer = 0.0
        # the timer interval between each frame
        self.interval = 0.0
        # initial frame
        self.frame = 0
        # total number of frames
        self.frames = 0
        # whether to follow the domain object through a teleporter
        self.follow = False
        # subclasess must call either sync_coordinate or sync_cell before they exit their __init__

    def update(self, elapsed_time):
        # update animation frame
        self.update_image(elapsed_time)
        # check the command queue for any commands
        if len(self.command_queue) > 0:
            # there is a command, get it
            command = self.command_queue[0]
            command_name = self.command_name(command)
            # command evaluations
            if command_name == 'Stall':
                # stall does nothing and doesn't remove itself so it effectively suspends the object
                return
            elif command_name == 'Move_To':
                # move straight line to the destination in renderer map rect pixel coordinates
                destination = command.destination
                # check to see if within 1 pixel of destination
                if self.distance_from(destination) <= 1.0 + eps:
                    # arrived at destination
                    self.sync_coordinate(destination)
                    # remove this command item from the queue
                    self.command_queue.pop(0)
                else:
                    # move towards destination
                    self.move_towards(destination, elapsed_time)
            elif command_name == 'Teleport':
                # teleport to a new position
                destination = command.destination
                self.sync_cell(destination)
                self.command_queue.pop(0)
                # if follow then switch floor
                if self.follow:
                    self.domain_manager.switch_floor(self.domain_manager.get_floor(destination))
            elif command_name == 'Path':
                # insert a path into the command queue
                path = command.path
                # remove this command from the queue
                self.command_queue.pop(0)
                # replaces a path_to with move_to and teleport commands without affecting items in the queue after it
                # path is in reverse order, when inserted into the queue that results in the commands being in forward order
                for kind, value in path:
                    if kind == 'move':
                        # convert to renderer map rect pixel coordinates for each position in the path
                        self.command_queue.insert(0, Move_To(self.pixel_centre(value)))
                    elif kind == 'teleport':
                        self.command_queue.insert(0, Teleport(value))
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

    def distance_from(self, position):
        # distance between self and position
        return sqrt((abs(self.centre_xpos - position[0]) ** 2) + (abs(self.centre_ypos - position[1]) ** 2))

    def move_towards(self, destination, elapsed_time):
        # find the angle in radians to the destination
        angle = atan2(destination[1] - self.centre_ypos, destination[0] - self.centre_xpos)
        # move towards that angle in radians, by speed, and by elapsed time
        self.sync_coordinate((self.centre_xpos + ((cos(angle) * self.speed) * elapsed_time),
                              self.centre_ypos + ((sin(angle) * self.speed) * elapsed_time)))

    def pixel_centre(self, location):
        # given a tile x and y cell coordinate return the graphical x and y center point in renderer map rect pixels
        x_width, y_height = self.map_object.tilewidth, self.map_object.tileheight
        x_centre, y_centre = int(x_width / 2), int(y_height / 2)
        return (location[0] * x_width) + x_centre, (location[1] * y_height) + y_centre

    def sync_coordinate(self, position):
        # update position state in pixels
        self.centre_xpos, self.centre_ypos = position
        self.rect.center = int(self.centre_xpos), int(self.centre_ypos)
        self.coord = int(self.rect.centerx / self.map_object.tilewidth), int(self.rect.centery / self.map_object.tileheight)

    def sync_cell(self, position):
        # update position state in cells
        self.centre_xpos, self.centre_ypos = self.pixel_centre(position)
        self.rect.center = int(self.centre_xpos), int(self.centre_ypos)
        self.coord = position

    def load_tiles(self, tiles):
        # load a tile sequence from tile sheet as an animation
        self.animations = []
        for tile in tiles:
            self.animations.append(cut_tile(tile))
        self.frame = 0
        self.frames = len(self.animations)
        self.image = self.animations[self.frame]
        self.rect = self.animations[self.frame].get_rect()

    def update_image(self, elapsed_time):
        # handle animation frames
        if self.frames > 1:
            # add elapsed time to timer time
            self.timer += elapsed_time
            # if timer time is greater than frame time interval
            if self.timer >= self.interval:
                # remove the interval leaving the remainer for future times
                self.timer -= self.interval
                # adjust the frame of the domain object
                self.frame += 1
                # limit frames within indexes
                if self.frame >= self.frames:
                    self.frame = 0
                # update sprite image from frame
                self.image = self.animations[self.frame]
