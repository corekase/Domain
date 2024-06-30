import pygame
from pygame import Rect
from components.bundled.pyscroll.orthographic import BufferedRenderer
from components.bundled.pyscroll.data import TiledMapData
from components.bundled.pytmx.util_pygame import load_pygame
from components.utility import file_resource
from components.object.objectmanager import ObjectManager
from components.object.domainobject import DomainObject
from components.object.genericobject import GenericObject
from components.object.pickupobject import PickupObject
from components.object.agentobject import AgentObject
from components.object.avatarobject import AvatarObject
from components.object.teleporterobject import TeleporterObject
from random import randint

# named indexes for tiles to map the correct gid
EMPTY, FLOOR, WALL = 0, 1, 2

class DomainManager:
    # reference to the gui manager
    gui = None
    # reference to domain object manager
    domain = None
    # reference to tiles gid tuple
    tiles = None

    def __init__(self, view_surface):
        # load the map
        self.map = load_pygame(file_resource('domains', 'domain.tmx'))
        # give MapObject subclasses a common reference to the map
        DomainObject.map = self.map
        self.view_surface = view_surface
        self.view_surface_rect = view_surface.get_rect()
        size = self.view_surface.get_rect().width, self.view_surface.get_rect().height
        self.renderer = BufferedRenderer(TiledMapData(self.map), size, False)
        # set the zoom levels for the renderer
        self.zoom_amounts_index = 0
        self.zoom_amounts = [1.0, 2.0, 4.0]
        self.renderer.zoom = self.zoom_amounts[self.zoom_amounts_index]
        # create an object manager
        self.domain = ObjectManager(self.renderer)
        # share that domain with map objects
        DomainObject.domain = self.domain
        # add in teleporters
        teleporters = {(27, 2): [1, 'up', (57, 2)],
                       (57, 2): [0, 'down', (27, 2)],
                       (32, 27): [2, 'up', (62, 27)],
                       (62, 27): [1, 'down', (32, 27)]}
        for teleporter, info in teleporters.items():
            # destination floor the teleport leads to
            dest_floor = info[0]
            # whether to show an up or down graphic
            up_down = info[1]
            # destination coordinate for the teleport in cells
            destination = info[2]
            # instantiate the teleport
            instance = TeleporterObject(dest_floor, up_down, teleporter, destination)
            instance.layer = 4
            # add it to the domain
            self.domain.object_add('teleporters', instance)
        # helper function to create objects
        def populate(number, cls, layer, group):
            for floor in range(3):
                for _ in range(number):
                    position = self.find_random_position_floor(DomainManager.tiles[FLOOR], floor, 30)
                    # instantiate from the class
                    instance = cls(floor, position)
                    # set the layer, higher takes priority
                    instance.layer = layer
                    # add the instance to the group
                    self.domain.object_add(group, instance)
        # create generic items
        populate(20, GenericObject, 1, 'generic')
        # create pickup items
        populate(1, PickupObject, 2, 'pickups')
        # create agents
        populate(4, AgentObject, 3, 'agents')
        # create a player avatar and add it to the domain
        position = self.find_random_position_floor(DomainManager.tiles[FLOOR], 0, 30)
        self.avatar = AvatarObject(0, position)
        self.avatar.domain_manager = self
        self.avatar.layer = 5
        self.domain.object_add('avatar', self.avatar)
        # set main viewport to avatar center, within map view bounds
        self.main_viewport = list(self.avatar.rect.center)
        # map constants
        self.floor_tiles = 30
        floor_size = int(self.map.width / self.floor_tiles)
        # each floor_ports is a rect which has the boundaries for the floor
        self.floor_ports = []
        # these values stay the same for each floor_port
        width = self.floor_tiles * self.map.tilewidth
        y_size = self.map.tileheight * self.floor_tiles
        # find a rect for each floor
        for floor in range(floor_size):
            x_base = floor * (self.floor_tiles * self.map.tilewidth)
            self.floor_ports.append(Rect(x_base, 0, width, y_size))
        # initial floor_port is none
        self.floor_port = None
        # initial floor is none
        self.floor = None
        # switch to avatar floor and location
        self.switch_floor(self.get_floor(self.avatar.x_coord))
        self.main_viewport = list(self.avatar.rect.center)

    def find_random_position_floor(self, gid, floor, floor_size):
        return self.find_random_position(gid, floor * floor_size, floor_size, 0, floor_size)

    def find_random_position(self, gid, x_min, width, y_min, height):
        # return a random cell position which contains a specific tile gid
        while True:
            x, y = randint(x_min, x_min + width - 1), randint(y_min, y_min + height - 1)
            hit = False
            for item in self.domain.domain():
                if item.x_coord == x and item.y_coord == y:
                    hit = True
                    continue
            if hit:
                continue
            if self.find_cell_gid((x, y)) == gid:
                return x, y

    def find_cell_gid(self, position):
        # get the tile gid for a cell position
        x, y = position
        if x < 0 or y < 0 or x >= DomainObject.map.width or y >= DomainObject.map.height:
            return None
        return DomainObject.map.get_tile_gid(x, y, 0)

    def find_cell_objects(self, position, objects):
        # return a list of objects which match the position coordinate
        results = []
        x, y = position
        for item in objects:
            if (item.x_coord == x) and (item.y_coord == y):
                results.append(item)
        return results

    def switch_floor(self, floor):
        # get distance from center of current floor
        if self.floor != None:
            x, y = self.floor_ports[self.floor].center
            difx = self.main_viewport[0] - x
            dify = self.main_viewport[1] - y
        else:
            difx, dify = 0, 0
        # load new floor
        self.floor = floor
        self.floor_port = self.floor_ports[self.floor]
        # add the difference to new center of floor
        x, y = self.floor_port.center
        self.main_viewport[0], self.main_viewport[1] = x + difx, y + dify
        self.draw_domain()

    def get_floor(self, x_cell):
        return int(x_cell / self.floor_tiles)

    def update_domain(self, elapsed_time):
        # check for other mapobject collision, the sprites group is an expensive operation
        # so is done once on its own line here
        objects = self.domain.domain().sprites()
        for object in objects:
            # same, done once on its own line because it's an expensive operation
            other_objects = pygame.sprite.spritecollide(object, self.domain.domain(), False)
            for other_object in other_objects:
                if not (other_object is object):
                    # right here for finer-collisions:
                    #     "if overlapped then per-pixel (mask-based) comparison"
                    # for overall fast collisions and then accuracy only when overlapped
                    object.overlap(other_object)
                    other_object.overlap(object)
        # update all mapobjects and their subclasses in the domain group
        self.domain.domain().update(elapsed_time)

    def pick_cell(self, x, y):
        # normalize x and y mouse position to the screen coordinates of the surface
        x_pos, y_pos = x - self.view_surface_rect.centerx, y - self.view_surface_rect.centery
        # get all the needed information from the map and renderer
        x_tile_size = self.map.tilewidth * self.renderer.zoom
        y_tile_size = self.map.tileheight * self.renderer.zoom
        map_centre_x = self.renderer.map_rect.centerx * self.renderer.zoom
        map_centre_y = self.renderer.map_rect.centery * self.renderer.zoom
        view_centre_x = self.renderer.view_rect.centerx * self.renderer.zoom
        view_centre_y = self.renderer.view_rect.centery * self.renderer.zoom
        # go through each geometry frame ending at the x and y mouse position
        relative_x = map_centre_x - view_centre_x - x_pos
        relative_y = map_centre_y - view_centre_y - y_pos
        # divide those into tile sizes to get a coordinate
        x_coord, y_coord = relative_x / x_tile_size, relative_y / y_tile_size
        # convert that screen coordinate into an array coordinate for programming
        x_coord = int(-x_coord + self.map.width / 2)
        y_coord = int(-y_coord + self.map.height / 2)
        # coordinates are now in map array indexes
        return x_coord, y_coord

    def set_zoom_index(self, index_delta):
        # clamp index inside zoom_amounts list.
        self.zoom_amounts_index = max(0, min(self.zoom_amounts_index + index_delta,
                                             len(self.zoom_amounts) - 1))
        # update state information inside the renderer
        self.renderer.zoom = self.zoom_amounts[self.zoom_amounts_index]

    def draw_domain(self):
        # centre on desired viewport
        self.renderer.center(self.main_viewport)
        # if horizontal out-of-bounds limit them
        if self.renderer.view_rect.left < self.floor_port.left:
            self.renderer.view_rect.left = self.floor_port.left
        elif self.renderer.view_rect.right > self.floor_ports[self.floor].x + self.floor_port.width:
            self.renderer.view_rect.right = self.floor_ports[self.floor].x + self.floor_port.width
        # if vertical out-of-bounds limit them
        if self.renderer.view_rect.top < self.floor_port.top:
            self.renderer.view_rect.top = self.floor_port.top
        elif self.renderer.view_rect.bottom > self.floor_port.bottom:
            self.renderer.view_rect.bottom = self.floor_port.bottom
        # get main viewport coordinates from the renderer view rect
        self.main_viewport[0], self.main_viewport[1] = self.renderer.view_rect.center
        # align view centre to pixel coordinates by converting them to ints
        self.main_viewport[0], self.main_viewport[1] = int(self.main_viewport[0]), int(self.main_viewport[1])
        # reupdate the viewport, viewport is updated here in case the bounds were modified
        self.renderer.center(self.main_viewport)
        # draw map and group objects to surface
        self.domain.domain().draw(self.view_surface)
