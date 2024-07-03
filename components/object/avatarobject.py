from .domainobject import DomainObject, Path_To, Datagram, Teleport
from ..utility import image_alpha_resource

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
            pickups = DomainObject.domain_manager.cell_objects((self.x_coord, self.y_coord), DomainObject.domain.objects('pickups'))
            if len(pickups) > 0:
                # enable pick up button
                DomainObject.gui.switch_context('pickup_context')
        else:
            # check current cell for any teleporters
            teleport = DomainObject.domain_manager.teleporters((self.x_coord, self.y_coord))
            if teleport == None:
                # enable put down button
                DomainObject.gui.switch_context('putdown_context')

    def move_to(self, position):
        # switch to default context while moving
        DomainObject.gui.switch_context('default')
        # perform move
        if self.reset_queue():
            # no move_to in the queue so just go there directly
            self.move_to_guarded(position)
        else:
            # do after existing move_to
            self.command(Datagram(self.move_to_guarded, position))

    def move_to_guarded(self, position):
        # from current position go to new_position
        self.command(Path_To(position))
        teleport = DomainObject.domain_manager.teleporters(position)
        if teleport != None:
            # there is a teleporter at the new position
            self.command(Teleport(teleport, True))

    def pick_up(self):
        # pick up inventory
        pickup = DomainObject.domain_manager.cell_objects((self.x_coord, self.y_coord), DomainObject.domain.objects('pickups'))[0]
        self.inventory = pickup
        # delete pickup object from the domain
        DomainObject.domain.delete('pickups', pickup)

    def put_down(self):
        # update the pickup object coordinates
        self.inventory.sync_cell((self.x_coord, self.y_coord))
        # place the pickup object back into the domain
        DomainObject.domain.object_add('pickups', self.inventory)
        # delete inventory
        self.inventory = None
