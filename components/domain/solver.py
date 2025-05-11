class Coordinate:
    # coordinate container for find_path() when only one destination is needed
    def __init__(self, position):
        self.coord = position

class Solver:
    # this class is where various problem solving methods go
    # neighbours are for find_path, the tuple indexes map like this:
    # 0 1 2
    # 3 4 5
    # 6 7 8
    # indexes are delta x and y coordinates around 4 which is the centre point
    neighbours = ((-1, -1), (0, -1), (1, -1),
                  (-1,  0), (0,  0), (1,  0),
                  (-1,  1), (0,  1), (1,  1))

    def __init__(self, domain):
        from components.bundled.pytmx import TiledMap
        from components.bundled.pyscroll.orthographic import BufferedRenderer
        # which domain manager the solver is attached to
        self.domain_manager = domain
        # the map object of that domain
        self.map_object:TiledMap = domain.map_object
        # and its renderer
        self.renderer:BufferedRenderer = domain.renderer
        # the rect for the domain graphical area
        self.surface_rect = domain.surface_rect
        # the gid for which tile is a floor tile
        self.floor_gid = domain.floor_gid

    def pixel_to_cell(self, x, y):
        # convert a pixel coordinate within the drawing area to a cell coordinate for indexing
        # normalize x and y mouse position to the centre of the surface rect, in screen pixels
        x_pos, y_pos = x - self.surface_rect.centerx, y - self.surface_rect.centery
        # get all the needed information from the map and renderer, scaled to screen pixels
        x_tile_size = self.map_object.tilewidth * self.renderer.zoom
        y_tile_size = self.map_object.tileheight * self.renderer.zoom
        map_centre_x = self.renderer.map_rect.centerx * self.renderer.zoom
        map_centre_y = self.renderer.map_rect.centery * self.renderer.zoom
        view_centre_x = self.renderer.view_rect.centerx * self.renderer.zoom
        view_centre_y = self.renderer.view_rect.centery * self.renderer.zoom
        # go through each geometry frame ending at the x and y mouse position
        relative_x = map_centre_x - view_centre_x - x_pos
        relative_y = map_centre_y - view_centre_y - y_pos
        # divide those into tile sizes to get cartesian coordinates
        x_coord, y_coord = relative_x / x_tile_size, relative_y / y_tile_size
        # convert cartesian coordinates into array indexes for programming
        x_coord = int(-x_coord + (self.map_object.width / 2))
        y_coord = int(-y_coord + (self.map_object.height / 2))
        # coordinates are now in array indexes
        return x_coord, y_coord

    def find_path(self, start_position, destinations):
        # solve a path from a start to multiple destinations and return shortest
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
            for item in destinations:
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
            teleporter = self.domain_manager.teleporters(current)
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
            # create list of valid neighbours from the current cell
            adjacents = []
            # fill list with cell positions by adding neighbour deltas to each axis
            for neighbour in self.neighbours:
                adjacents.append(self.domain_manager.cell_gid((current[0] + neighbour[0], current[1] + neighbour[1])))
            # block out invalid moves depending on present floor tiles
            if adjacents[1] != self.floor_gid:
                adjacents[0] = None
                adjacents[2] = None
            if adjacents[5] != self.floor_gid:
                adjacents[2] = None
                adjacents[8] = None
            if adjacents[7] != self.floor_gid:
                adjacents[6] = None
                adjacents[8] = None
            if adjacents[3] != self.floor_gid:
                adjacents[0] = None
                adjacents[6] = None
            # add neighbours that are floor tiles to the frontier, the order affects how straight the paths are
            for index in (1, 5, 7, 3, 2, 8, 6, 0):
                # if it is a floor tile
                if adjacents[index] == self.domain_manager.floor_gid:
                    new_position = current[0] + self.neighbours[index][0], current[1] + self.neighbours[index][1]
                    # if the neighbour is on the same floor then it is valid
                    if self.domain_manager.get_floor(current) == self.domain_manager.get_floor(new_position):
                        # if the cell hasn't been previously visited then add it to the frontier
                        if new_position not in came_from:
                            frontier.append(new_position)
                            # track the flow of the cell
                            came_from[new_position] = current
        if found:
            # path between goal and start
            path = []
            # is there a teleporter at the goal?
            teleporter = self.domain_manager.teleporters(goal)
            if teleporter != None:
                # if so, add that teleport to the path
                destination = teleporter.destination
                path.append(('teleport', destination))
            # get a list of the tracked teleport coordinates
            teleports = teleport_destinations.keys()
            # follow the flow back to the start
            while goal != start_position:
                # is this cell a teleport?
                if goal in teleports:
                    path.append(('teleport', teleport_destinations[goal]))
                # otherwise it's a move
                else:
                    path.append(('move', goal))
                # follow flow
                goal = came_from[goal]
            # path is in reverse order, goal to start
            return path, goal_object
        else:
            # no valid path found
            return None, None
