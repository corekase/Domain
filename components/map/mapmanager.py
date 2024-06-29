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

class MapManager:
    # reference to the gui manager
    gui = None

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
        self.zoom_amounts_index = 1
        self.zoom_amounts = [1.0, 2.0, 4.0]
        self.renderer.zoom = self.zoom_amounts[self.zoom_amounts_index]
        # create an object manager
        self.domain = ObjectManager(self.renderer)
        # share that domain with map objects
        DomainObject.domain = self.domain
        # helper function to create objects
        def populate(number, cls, layer, group):
            for _ in range(number):
                # instantiate from the class
                instance = cls()
                # set the layer, higher takes priority
                instance.layer = layer
                # add the instance to the group
                self.domain.object_add(group, instance)
        # create generic items
        populate(30, GenericObject, 1, 'generic')
        # create pickup items
        populate(3, PickupObject, 2, 'pickups')
        # create agents
        populate(0, AgentObject, 3, 'agents')
        # create a player avatar and add it to the domain
        self.avatar = AvatarObject()
        self.avatar.layer = 4
        self.domain.object_add('avatar', self.avatar)
        # set main viewport to avatar center, within map view bounds
        self.main_viewport = list(self.avatar.rect.center)
        # build border left, right, and up, down, for each floor
        floor_tiles = 30
        floor_size = int(self.map.width / floor_tiles)
        # floors is a list of rects which are the map pixel boundaries for each
        self.floors = []
        for floor in range(floor_size):
            x_base = floor_tiles * floor * self.map.tilewidth - (self.map.tilewidth / 2)
            visible = floor_tiles * self.map.tilewidth
            x_upper = x_base + visible + (self.map.tilewidth)
            y_upper = self.map.tileheight * floor_tiles + (self.map.tileheight)
            self.floors.append(Rect(x_base, 0 - (self.map.tileheight / 2), x_upper, y_upper))
        self.floor_port = None
        self.floor = 0
        self.switch_floor(self.floor)

    def switch_floor(self, floor):
        if floor >= 0 and floor < len(self.floors):
            self.floor = floor
            self.floor_port = self.floors[self.floor]

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
        width = (self.map.tilewidth * 32) / self.renderer.zoom
        height = (self.map.tileheight * 32) / self.renderer.zoom
        main_rect = Rect(0, 0, width, height)
        main_rect.center = self.main_viewport
        base_x = self.floor * self.map.tilewidth
        max_x = self.floor_port.width
        # if horizontal out-of-bounds limit them
        if main_rect.left < self.floor_port.left:
            main_rect.left = self.floor_port.left
        elif main_rect.right > base_x + max_x:
            main_rect.right = base_x + max_x
        # if vertical out-of-bounds limit them
        if main_rect.top < self.floor_port.top:
            main_rect.top = self.floor_port.top
        elif main_rect.bottom > self.floor_port.bottom:
            main_rect.bottom = self.floor_port.bottom
        # align view centre to pixel coordinates by converting them to ints
        self.main_viewport[0], self.main_viewport[1] = list(main_rect.center)
        # reupdate the viewport, viewport is updated here in case the bounds were modified
        self.renderer.center(self.main_viewport)
        # draw map and group objects to surface
        self.domain.domain().draw(self.view_surface)
