import pygame
from random import randint
from .solver import Solver

class DomainManager:
    # reference to tile_gid tuple
    floor_gid = None
    # floor push button group
    floor_group = None

    def __init__(self, surface):
        # needed functions for initialization
        from components.bundled.pytmx.util_pygame import load_pygame
        from components.utility import file_resource
        from components.bundled.pyscroll.orthographic import BufferedRenderer
        from components.bundled.pyscroll.data import TiledMapData
        from pygame import Rect
        # object references needed for domain initialization
        from components.object.domainobject import DomainObject
        from components.object.objectmanager import ObjectManager
        from components.object.teleporter import Teleporter
        from components.object.generic import Generic
        from components.object.pickup import Pickup
        from components.object.agent import Agent
        from components.object.avatar import Avatar
        # load the map, map is a keyword so this has _object added
        self.map_object = load_pygame(file_resource('domains', 'domain.tmx'))
        # give DomainObject subclasses a common reference to the map
        DomainObject.map_object = self.map_object
        # known position for floor tile on the map
        floor_tile = (0, 0)
        # read that position and store the gid in both DomainManager and DomainObject as floor_gid
        DomainManager.floor_gid = DomainObject.floor_gid = self.cell_gid(floor_tile)
        # surface to draw on
        self.surface = surface
        self.surface_rect = surface.get_rect()
        size = self.surface_rect.width, self.surface_rect.height
        # reference to the renderer
        self.renderer = BufferedRenderer(TiledMapData(self.map_object), size, False)
        # set the zoom levels for the renderer
        self.zoom_amounts_index = 2
        self.zoom_amounts = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
        self.renderer.zoom = self.zoom_amounts[self.zoom_amounts_index]
        # create an object manager
        self.object_manager = ObjectManager(self.renderer)
        # share the object manager with domain objects
        DomainObject.object_manager = self.object_manager
        # map constants
        self.floor_tiles = 30
        self.floors = int(self.map_object.width / self.floor_tiles)
        # each floor_ports is a rect which has the boundaries for the floor
        self.floor_ports = []
        # size of the floor port, square maps and tiles are assumed here, adjust if needed
        self.floor_size = self.floor_tiles * self.map_object.tilewidth
        # define a rect for each floor port
        for floor in range(self.floors):
            x_base = floor * self.floor_size
            self.floor_ports.append(Rect(x_base, 0, self.floor_size, self.floor_size))
        # initial floor_port is none
        self.floor_port = None
        # initial floor is none
        self.floor = None
        # add in teleporters, 'teleporters' is a reserved group name, the domain manager uses it
        # so other code may not use that group name
        for item in self.map_object.objects:
            if item.type == 'Teleporter':
                # x and y of the teleporter in cell coordinates
                position = (int(item.x / self.map_object.tilewidth), int(item.y / self.map_object.tileheight))
                # destination of the teleporter in cell coordinates
                destination = (int(item.properties['dest_x']), int(item.properties['dest_y']))
                # create a teleporter object
                instance = Teleporter(position, destination)
                # and set its layer
                instance.layer = 3
                # add the teleporter to the teleporters group
                self.object_manager.object_add('teleporters', instance)
            # elif for more object types
            else:
                raise Exception(f'Object: {item.type} not recognized')
        # helper function to create objects
        def populate(number, cls, layer, group):
            for floor in range(self.floors):
                for _ in range(number):
                    position = self.random_position_floor(self.floor_gid, floor)
                    # instantiate from the class
                    instance = cls(position)
                    # set the layer, higher takes priority
                    instance.layer = layer
                    # add the instance to the group
                    self.object_manager.object_add(group, instance)
        # create generic items
        populate(15, Generic, 1, 'generic')
        # create pickup items
        populate(1, Pickup, 2, 'pickups')
        # create agents
        populate(4, Agent, 4, 'agents')
        # create a player avatar and add it to the domain
        position = self.random_position_floor(self.floor_gid, 0)
        self.avatar = Avatar(position)
        self.avatar.layer = 5
        self.object_manager.object_add('avatar', self.avatar)
        # initialize the main viewport with any value, needed for switch_floor
        self.main_viewport = list([0, 0])
        # switch to the avatar floor, which will adjust main_viewport
        self.switch_floor(self.get_floor(self.avatar.coord))
        # centre the main_viewport on the avatar
        self.main_viewport = list(self.avatar.rect.center)
        # create a solver
        self.solver = Solver(self)

    # solver
    def pixel_to_cell(self, x, y):
        return self.solver.pixel_to_cell(x, y)

    # solver
    def find_path(self, start_position, destinations):
        return self.solver.find_path(start_position, destinations)

    def random_position(self, gid, x_min, y_min, width, height):
        # return a random empty cell position which is a specific tile gid
        while True:
            # random position
            position = randint(x_min, x_min + width - 1), randint(y_min, y_min + height - 1)
            # is it the correct gid
            if self.cell_gid(position) == gid:
                # is it already occupied by something
                hit = False
                for item in self.object_manager.domain():
                    if item.coord == position:
                        hit = True
                        break
                if hit:
                    continue
                # is correct gid and is empty
                return position

    def random_position_floor(self, gid, floor):
        return self.random_position(gid, floor * self.floor_tiles, 0, self.floor_tiles, self.floor_tiles)

    def get_floor(self, coord):
        return int(coord[0] / self.floor_tiles)

    def switch_floor(self, floor):
        # get distance from centre of current floor
        if self.floor != None:
            x, y = self.floor_ports[self.floor].center
            difx = self.main_viewport[0] - x
            dify = self.main_viewport[1] - y
        else:
            difx, dify = 0, 0
        # load new floor
        self.floor = floor
        self.floor_port = self.floor_ports[self.floor]
        # add the difference to new centre of floor
        x, y = self.floor_port.center
        self.main_viewport[0], self.main_viewport[1] = x + difx, y + dify
        # if there is a floor group then update it
        if self.floor_group != None:
            # update the floor push button group selection
            self.floor_group[self.floor].select()

    def cell_gid(self, position):
        # get the tile gid for a cell position
        x, y = position
        if x < 0 or y < 0 or x >= self.map_object.width or y >= self.map_object.height:
            return None
        return self.map_object.get_tile_gid(x, y, 0)

    def cell_objects(self, position, objects):
        # return a list of objects which match the position coordinate
        results = []
        for item in objects:
            if item.coord == position:
                results.append(item)
        return results

    def teleporters(self, position):
        # if there is a teleporter at position then return its destination otherwise return None
        teleporters = self.cell_objects(position, self.object_manager.objects('teleporters'))
        if len(teleporters) > 0:
            # there is a teleporter here, return the first match
            return teleporters[0]
        else:
            return None

    def check_win(self):
        # if all the pickup items are in the same cell then the game is won
        matched = True
        last_item = None
        objects = self.object_manager.objects('pickups')
        # if the avatar has an item in their inventory then include it
        if self.avatar.inventory != None:
            objects.append(self.avatar.inventory)
        # compare cell coordinates for all items, if any don't match then the check fails
        # the last item in the avatar inventory doesn't count until it's placed on the map
        # because its coordinates aren't updated until then
        for item in objects:
            if last_item == None:
                last_item = item
                continue
            if item.coord != last_item.coord:
                matched = False
                break
        # if true then won
        return matched

    def check_loss(self):
        # if the avatar sprite collides with any member of the agents group that is a loss
        if pygame.sprite.spritecollide(self.avatar, self.object_manager.objects('agents'),
                                       False, pygame.sprite.collide_mask):
            # collided
            return True
        # did not collide with any agents
        return False

    def set_zoom_delta(self, index_delta):
        # clamp index inside zoom_amounts list.
        old_index = self.zoom_amounts_index
        self.zoom_amounts_index = max(0, min(self.zoom_amounts_index + index_delta,
                                             len(self.zoom_amounts) - 1))
        # only adjust the renderer if the zoom changed to prevent flickering
        if self.zoom_amounts_index != old_index:
            # update state information inside the renderer
            self.renderer.zoom = self.zoom_amounts[self.zoom_amounts_index]
            if self.get_floor(self.avatar.coord) == self.floor:
                # centre on the avatar after a zoom change
                self.main_viewport = list(self.avatar.rect.center)

    def update_domain(self, elapsed_time):
        # update the domain
        self.object_manager.domain().update(elapsed_time)

    def draw_domain(self):
        # centre on desired viewport
        self.renderer.center(self.main_viewport)
        # if horizontal out-of-bounds limit them
        if self.renderer.view_rect.left < self.floor_port.left:
            self.renderer.view_rect.left = self.floor_port.left
        elif self.renderer.view_rect.right > self.floor_port.right:
            self.renderer.view_rect.right = self.floor_port.right
        # if vertical out-of-bounds limit them
        if self.renderer.view_rect.top < self.floor_port.top:
            self.renderer.view_rect.top = self.floor_port.top
        elif self.renderer.view_rect.bottom > self.floor_port.bottom:
            self.renderer.view_rect.bottom = self.floor_port.bottom
        # get main viewport coordinates from the renderer view rect
        self.main_viewport = list(self.renderer.view_rect.center)
        # reupdate the viewport, viewport is updated here in case the bounds were modified
        self.renderer.center(self.main_viewport)
        # draw map and group objects to surface
        self.object_manager.domain().draw(self.surface)
