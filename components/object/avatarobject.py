from .domainobject import DomainObject, Path_To, Datagram
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
        # check current cell for a pickup object
        if self.inventory == None:
            pickups = DomainObject.domain_manager.cell_objects((self.x_coord, self.y_coord), DomainObject.domain.objects('pickups'))
            if len(pickups) > 0:
                    # enable pick up button
                    DomainObject.gui.switch_context('pickup_context')
            else:
                # no pickups at location and no inventory, disable both contexts
                DomainObject.gui.switch_context(None)
        else:
            # enable put down button
            DomainObject.gui.switch_context('putdown_context')

    def move_to(self, position):
        # hide gui while moving
        DomainObject.gui.switch_context(None)
        # perform move
        if self.reset_queue():
            # no move_to in the queue so just go there directly
            self.move_to_stub(position)
        else:
            # do after existing move_to
            self.command(Datagram(self.move_to_stub, position))

    def move_to_stub(self, new_position):
        # from current position go to new_position
        self.command(Path_To(new_position))

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
