from .domainobject import DomainObject

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
        # switch to default context while moving
        self.gui_manager.switch_context('default')
        # perform move
        if self.reset_queue():
            # no move_to in the queue so just go there directly
            self.move_to_guarded(position)
        else:
            from .domainobject import Datagram
            # do after existing move_to
            self.command(Datagram(self.move_to_guarded, position))

    def move_to_guarded(self, position):
        from .domainobject import Path_To
        # from current position go to new_position
        self.command(Path_To(position))

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
