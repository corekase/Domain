class Coordinate:
    # coordinate container for find_path() when only one destination is needed
    def __init__(self, position):
        self.coord = position

class Solver():
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
        from components.domain.domainmanager import DomainManager
        self.domain_manager: DomainManager = domain
        self.floor_gid = self.domain_manager.floor_gid

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
