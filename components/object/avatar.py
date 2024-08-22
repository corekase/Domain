from .domainobject import DomainObject, Path
from components.domain.domainmanager import Coordinate

# named indexes for tiles to map the correct gid
FLOOR, WALL = 0, 1

class Avatar(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load tile animated sequence
        tiles = [(36, 68), (37, 68), (38, 68), (39, 68)]
        self.load_tiles(tiles)
        # interval between tile images
        self.interval = 0.08
        # world pixels per second
        self.speed = 64.0
        # sync position state
        self.sync_cell(position)
        # avatar inventory
        self.inventory = None

    def process(self):
        if self.inventory == None:
            # check current cell for a pickup object
            pickups = self.domain_manager.cell_objects(self.coord, self.object_manager.objects('pickups'))
            if len(pickups) > 0:
                # enable pick up button
                self.gui_manager.switch_context('pickup_context')
        else:
            # check current cell for any teleporters
            teleport = self.domain_manager.teleporters(self.coord)
            if teleport == None:
                # enable put down button
                self.gui_manager.switch_context('putdown_context')

    def move_to(self, position):
        if self.domain_manager.cell_gid(position) == self.tile_gid[FLOOR]:
            # perform move
            destination = self.reset_queue()
            if destination == None:
                # there is no move to in the queue, pathfind from current coordinate
                path = self.domain_manager.find_path(self.coord, [Coordinate(position)])[0]
            else:
                # there is a move to, pathfind from its destination after it completes
                path = self.domain_manager.find_path(destination, [Coordinate(position)])[0]
            if path != None:
                # switch to default context while moving
                self.gui_manager.switch_context('default')
                # add path to the command queue
                self.command(Path(path))

    def reset_queue(self):
        # clear the queue except for the first in-progress move to
        if len(self.command_queue) > 0:
            # get the current command
            current = self.command_queue[0]
            if self.command_name(current) == 'Move_To':
                # if it's a move to return its destination in cell coordinates and clear the queue except for it
                destination = current.destination
                coord = int(destination[0] / self.map_object.tilewidth), int(destination[1] / self.map_object.tileheight)
                self.command_queue = [current]
                return coord
        # otherwise clear the entire queue and return None
        self.command_queue = []
        return None

    def pick_up(self):
        # pick up inventory
        pickup = self.domain_manager.cell_objects(self.coord, self.object_manager.objects('pickups'))[0]
        self.inventory = pickup
        # delete pickup object from the domain
        self.object_manager.delete('pickups', pickup)

    def put_down(self):
        # update the pickup object coordinates
        self.inventory.sync_cell(self.coord)
        # place the pickup object back into the domain
        self.object_manager.object_add('pickups', self.inventory)
        # delete inventory
        self.inventory = None
