# named indexes for tiles to map the correct gid
EMPTY, WALL, FLOOR = 0, 1, 2

class Coordinate:
    # coordinate container for find_path() when only one destination is needed
    def __init__(self, position):
        self.coord = position

class DomainManager:
    # reference to tile_gid tuple
    tile_gid = None
    # reference to gui objects for floor control
    floor_group = None

    def __init__(self, view_surface):
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
        # surface to draw on
        self.view_surface = view_surface
        self.view_surface_rect = view_surface.get_rect()
        size = self.view_surface_rect.width, self.view_surface_rect.height
        # reference to the renderer
        self.renderer = BufferedRenderer(TiledMapData(self.map_object), size, False)
        # set the zoom levels for the renderer
        self.zoom_amounts_index = 0
        self.zoom_amounts = [2.0, 4.0, 8.0]
        self.renderer.zoom = self.zoom_amounts[self.zoom_amounts_index]
        # create an object manager
        self.object_manager = ObjectManager(self.renderer)
        # share the object manager with domain objects
        DomainObject.object_manager = self.object_manager
        # map constants
        self.floor_tiles = 60
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
        teleporters = {(1, 1): ['up', (61, 1)],
                       (61, 1): ['down', (1, 1)],
                       (58, 1): ['up', (118, 1)],
                       (118, 1): ['down', (58, 1)],
                       (1, 58): ['up', (61, 58)],
                       (61, 58): ['down', (1, 58)],
                       (58, 58): ['up', (118, 58)],
                       (118, 58): ['down', (58, 58)],
                       (29, 28): ['up', (89, 28)],
                       (89, 28): ['down', (29, 28)]}
        for position, info in teleporters.items():
            # whether to show an up or down graphic and destination coordinate for the teleport in cells
            up_down, destination = info
            # instantiate the teleport
            instance = Teleporter(up_down, position, destination)
            instance.layer = 3
            # add it to the domain, in 'teleporters' reserved name
            self.object_manager.object_add('teleporters', instance)
        # helper function to create objects
        def populate(number, cls, layer, group):
            for floor in range(self.floors):
                for _ in range(number):
                    position = self.random_position_floor(self.tile_gid[FLOOR], floor)
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
        populate(8, Agent, 4, 'agents')
        # create a player avatar and add it to the domain
        position = self.random_position_floor(self.tile_gid[FLOOR], 0)
        self.avatar = Avatar(position)
        self.avatar.layer = 5
        self.object_manager.object_add('avatar', self.avatar)
        # initialize the main viewport with any value, needed for switch_floor
        self.main_viewport = list([0, 0])
        # switch to the avatar floor, which will adjust main_viewport
        self.switch_floor(self.get_floor(self.avatar.coord))
        # centre the main_viewport on the avatar
        self.main_viewport = list(self.avatar.rect.center)

    def random_position(self, gid, x_min, y_min, width, height):
        from random import randint
        # return a random empty cell position which is a specific tile gid
        while True:
            # random position
            x, y = randint(x_min, x_min + width - 1), randint(y_min, y_min + height - 1)
            # is it the correct gid
            if self.cell_gid((x, y)) == gid:
                # is it already occupied by something
                hit = False
                for item in self.object_manager.domain():
                    if item.coord == (x, y):
                        hit = True
                        break
                if hit:
                    continue
                # is correct gid and is empty
                return x, y

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
        # update the floor select gui buttons
        if self.floor == 0:
            self.floor_group['0'].select()
        elif self.floor == 1:
            self.floor_group['1'].select()

    def find_path(self, start_position, destination_objects):
        frontier = [start_position]
        came_from = {}
        came_from[start_position] = goal = goal_object = None
        teleport_destinations = {}
        used_teleporters = []
        found = False
        while len(frontier) > 0:
            # get the frontier cell coordinate
            current = frontier.pop(0)
            # compare that coordinate against all destination objects
            for item in destination_objects:
                if item.coord == current:
                    # destination object is found
                    found = True
                    goal = current
                    goal_object = item
                    # break for loop
                    break
            if found:
                # if found, also break while loop
                break
            # check if there is a teleporter at the current cell
            teleporter = self.teleporters(current)
            if teleporter != None:
                # get source and destination cell coordinates
                source, destination = teleporter.coord, teleporter.destination
                if source not in used_teleporters:
                    # add them to used, only allowed to use a teleporter pair once
                    used_teleporters.append(source)
                    used_teleporters.append(destination)
                    if destination not in frontier:
                        # add the teleporter destination cell to the frontier
                        frontier.append(destination)
                        came_from[destination] = current
                        # track teleport coordinate for the path
                        teleport_destinations[destination] = destination
            # get list of valid neighbours from the current cell
            neighbours = self.adjacents(current)
            # add each valid neighbour into the frontier
            for next in neighbours:
                if next not in came_from:
                    frontier.append(next)
                    # track the flow of the cell
                    came_from[next] = current
        if found:
            # path between goal and start
            path = []
            # is there a teleporter at the goal?
            teleporter = self.teleporters(goal)
            if teleporter != None:
                # if so, add that teleport to the path
                destination = teleporter.destination
                path.append(['teleport', destination])
            # get a list of the tracked teleport coordinates
            teleports = teleport_destinations.keys()
            # follow the flow back to the start
            while goal != start_position:
                # is this cell a teleport?
                if goal in teleports:
                    path.append(['teleport', teleport_destinations[goal]])
                # otherwise it's a move
                else:
                    path.append(['move', goal])
                # follow flow
                goal = came_from[goal]
            # path is in reverse order, goal to start
            return path, goal_object
        else:
            # no valid path found
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
            adjacents.append(self.cell_gid((x + neighbour[0], y + neighbour[1])))
        # the list indexes map by the neighbour deltas as given in this diagram:
        # 0 1 2
        # 3 4 5
        # 6 7 8
        # with the layout order, block out invalid orthographic moves due to walls
        if adjacents[1] == self.tile_gid[WALL]:
            adjacents[0] = None
            adjacents[2] = None
        if adjacents[5] == self.tile_gid[WALL]:
            adjacents[2] = None
            adjacents[8] = None
        if adjacents[7] == self.tile_gid[WALL]:
            adjacents[6] = None
            adjacents[8] = None
        if adjacents[3] == self.tile_gid[WALL]:
            adjacents[0] = None
            adjacents[6] = None
        # order to return the adjacents in, this affects how appealing the paths look
        indexes = (1, 5, 7, 3, 2, 8, 6, 0)
        # build list of neighbours that are floor tiles in index order
        valid_neighbours = []
        for index in indexes:
            if adjacents[index] == self.tile_gid[FLOOR]:
                new_x, new_y = x + neighbours[index][0], y + neighbours[index][1]
                # if the neighbour is on the same floor then it is valid
                if self.get_floor(position) == self.get_floor((new_x, new_y)):
                    valid_neighbours.append((new_x, new_y))
        # return neighbours which are floor tiles as cell positions, in order
        return valid_neighbours

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

    def pick_cell(self, x, y):
        # renderer view_rect size at a given zoom must not be larger than renderer map_rect size
        # at the same zoom. if greater, pick_cell() gives invalid results.
        # normalize x and y mouse position to the screen coordinates of the surface
        x_pos, y_pos = x - self.view_surface_rect.centerx, y - self.view_surface_rect.centery
        # get all the needed information from the map and renderer
        x_tile_size = self.map_object.tilewidth * self.renderer.zoom
        y_tile_size = self.map_object.tileheight * self.renderer.zoom
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
        x_coord = int(-x_coord + self.map_object.width / 2)
        y_coord = int(-y_coord + self.map_object.height / 2)
        # coordinates are now in map array indexes
        return x_coord, y_coord

    def set_zoom_index(self, index_delta):
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
        if self.renderer.view_rect.left <= self.floor_port.left:
            self.renderer.view_rect.left = self.floor_port.left
        elif self.renderer.view_rect.right >= self.floor_ports[self.floor].x + self.floor_port.width:
            self.renderer.view_rect.right = self.floor_ports[self.floor].x + self.floor_port.width
        # if vertical out-of-bounds limit them
        if self.renderer.view_rect.top <= self.floor_port.top:
            self.renderer.view_rect.top = self.floor_port.top
        elif self.renderer.view_rect.bottom >= self.floor_port.bottom:
            self.renderer.view_rect.bottom = self.floor_port.bottom
        # get main viewport coordinates from the renderer view rect
        self.main_viewport[0], self.main_viewport[1] = list(self.renderer.view_rect.center)
        # reupdate the viewport, viewport is updated here in case the bounds were modified
        self.renderer.center(self.main_viewport)
        # draw map and group objects to surface
        self.object_manager.domain().draw(self.view_surface)
