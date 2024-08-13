# bring in class references
from components.bundled.pytmx import TiledMap
from components.object.objectmanager import ObjectManager
from components.gui.guimanager import GuiManager
from components.domain.domainmanager import DomainManager
from math import cos, sin, radians, atan2, degrees, sqrt
from ..utility import sprite_sheet
import sys
eps = sys.float_info.epsilon

from collections import namedtuple
# commands and their parameters for the command queue
Stall = namedtuple('Stall', 'none')
Move_To = namedtuple('Move_To', 'destination')
Path_To = namedtuple('Path_To', 'path')
Teleport = namedtuple('Teleport', 'destination follow')

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
        self.rect = None
        self.centre_xpos, self.centre_ypos = None, None
        self.coord = None
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
                # from current coordinate follow path
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
                        is_avatar = self is self.domain_manager.avatar
                        self.command_queue.insert(0, Teleport(value, is_avatar))
            elif command_name == 'Teleport':
                # teleport to a new position
                destination, follow = command.destination, command.follow
                self.sync_cell(destination)
                self.command_queue.pop(0)
                # if follow then switch floor and main_viewport as well, done within a single command queue item
                if follow:
                    self.domain_manager.switch_floor(self.domain_manager.get_floor(destination))
                    self.domain_manager.main_viewport = list(self.rect.center)
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
        self.coord = int(self.rect.centerx / self.map_object.tilewidth), int(self.rect.centery / self.map_object.tileheight)

    def sync_cell(self, position):
        # update position state in cells
        self.centre_xpos, self.centre_ypos = self.pixel_centre(position)
        self.rect.center = int(self.centre_xpos), int(self.centre_ypos)
        self.coord = position

    def load_sheet(self, *image):
        # load the sprite sheet for this domain object
        self.animations = sprite_sheet(*image)
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
