# named indexes for tiles to map the correct gid
EMPTY, WALL, FLOOR = 0, 1, 2

from .domainobject import DomainObject
from components.domain.domainmanager import Coordinate

class AvatarObject(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load images
        self.load_sheet('sprites', 'avatar', 'avatar.png')
        # frame time
        self.interval = 0.2
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
                from .domainobject import Path_To
                self.command(Path_To(path))

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
