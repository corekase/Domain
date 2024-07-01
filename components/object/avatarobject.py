from .domainobject import DomainObject, Path_To, Datagram, Teleport, Switch_Floor
from ..utility import image_alpha_resource

class AvatarObject(DomainObject):
    def __init__(self, position):
        super().__init__()
        self.normal_image = image_alpha_resource('sprites', 'avatar', 'avatar_normal.png')
        self.overlap_image = self.normal_image
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.speed = 64.0
        self.sync_cell(position)
        # avatar inventory
        self.inventory = None

    def process(self):
        DomainObject.gui.switch_context(None)
        if self.inventory == None:
            # check current cell for a pickup object
            pickups = DomainObject.domain_manager.cell_objects((self.x_coord, self.y_coord), DomainObject.domain_objects.objects('pickups'))
            if len(pickups) > 0:
                # enable pick up button
                DomainObject.gui.switch_context('pickup_context')
        else:
            # check current cell for any teleporter
            teleporters = DomainObject.domain_manager.cell_objects((self.x_coord, self.y_coord), DomainObject.domain_objects.objects('teleporters'))
            if len(teleporters) == 0:
                # enable put down button
                DomainObject.gui.switch_context('putdown_context')

    def move_to(self, position):
        # hide gui while moving
        DomainObject.gui.switch_context(None)
        teleporters = DomainObject.domain_manager.cell_objects(position, DomainObject.domain_objects.objects('teleporters'))
        if len(teleporters) > 0:
            # there is a teleporter here
            teleport_destination = teleporters[0].destination
        else:
            teleport_destination = None
        # perform move
        if self.reset_queue():
            # no move_to in the queue so just go there directly
            self.move_to_guarded((position, teleport_destination))
        else:
            # do after existing move_to
            self.command(Datagram(self.move_to_guarded, (position, teleport_destination)))

    def move_to_guarded(self, parameters):
        new_position, teleport_destination = parameters
        # from current position go to new_position
        self.command(Path_To(new_position))
        if teleport_destination != None:
            # there is a teleporter at the new position
            self.command(Teleport(teleport_destination))
            self.command(Switch_Floor(DomainObject.domain_manager.get_floor(teleport_destination[0])))

    def pick_up(self):
        # pick up inventory
        pickup = DomainObject.domain_manager.cell_objects((self.x_coord, self.y_coord), DomainObject.domain_objects.objects('pickups'))[0]
        self.inventory = pickup
        # delete pickup object from the domain
        DomainObject.domain_objects.delete('pickups', pickup)

    def put_down(self):
        # update the pickup object coordinates
        self.inventory.sync_cell((self.x_coord, self.y_coord))
        # place the pickup object back into the domain
        DomainObject.domain_objects.object_add('pickups', self.inventory)
        # delete inventory
        self.inventory = None
