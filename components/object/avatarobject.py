from .mapobject import MapObject, Path_To, Datagram
from ..utility import image_alpha_resource

class AvatarObject(MapObject):
    def __init__(self):
        super().__init__()
        self.normal_image = image_alpha_resource('sprites', 'avatar', 'avatar_normal.png')
        self.overlap_image = self.normal_image
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.speed = 64.0
        # get random starting position
        position = self.find_random_position(MapObject.FLOOR)
        self.sync_cell(position)
        # avatar inventory
        self.inventory = None

    def process(self):
        # check current cell for a pickup object
        if self.inventory == None:
            pickups = self.find_cell_objects((self.x_coord, self.y_coord), MapObject.domain.objects('pickup'))
            if len(pickups) > 0:
                    # enable pick up button
                    MapObject.gui.switch_context('pickup_buttons')
            else:
                # no pickups at location and no inventory, disable both contexts
                MapObject.gui.switch_context(None)
        else:
            # enable put down button
            MapObject.gui.switch_context('putdown_buttons')

    def move_to(self, position):
        # manage context
        if self.inventory == None:
            MapObject.gui.switch_context(None)
        else:
            MapObject.gui.switch_context('putdown_buttons')
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
        pickup = self.find_cell_objects((self.x_coord, self.y_coord), MapObject.domain.objects('pickup'))[0]
        self.inventory = pickup
        # delete pickup object from the domain
        MapObject.domain.delete('pickup', pickup)

    def put_down(self):
        # put down inventory
        if self.reset_queue():
            # no move_to in queue, do directly
            self.put_down_stub(None)
        else:
            # do after move_to
            self.command(Datagram(self.put_down_stub, None))

    def put_down_stub(self, arg):
        # update the pickup object coordinates
        self.inventory.sync_cell((self.x_coord, self.y_coord))
        # place the pickup object back into the domain
        MapObject.domain.object_add('pickup', self.inventory)
        # delete inventory
        self.inventory = None
