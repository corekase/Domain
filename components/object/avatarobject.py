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
        x, y = self.find_random_position(MapObject.FLOOR)
        # translate x and y cell coordinates into world pixel coordinates, centered in the position
        self.centre_xpos, self.centre_ypos = self.tile_graphical_centre((x, y))
        # update position state with the translation
        self.rect_sync((self.centre_xpos, self.centre_ypos))
        # agent memory
        self.inventory = None

    def process(self):
        # check current cell for a pickup object
        if self.inventory == None:
            pickups = self.find_cell_objects((self.x_coord, self.y_coord), MapObject.domain.objects('pickup'))
            if len(pickups) > 0:
                    # enable pickup button
                    MapObject.gui.switch_context('pickup')
            else:
                # no pickups at location and no inventory, disable both contexts
                MapObject.gui.switch_context(None)
        else:
            # enable drop button
            MapObject.gui.switch_context('putdown')

    def move_to(self, position):
        # manage context
        if self.inventory == None:
            MapObject.gui.switch_context(None)
        else:
            MapObject.gui.switch_context('putdown')
        # perform move
        if self.reset_queue():
            # nothing in the queue so just go there directly
            self.path_to(position)
        else:
            # do after existing move_to
            self.command(Datagram(self.path_to, position))

    def path_to(self, new_position):
        # from current position go to new_position
        self.command(Path_To(new_position))

    def pick_up(self):
        # pick up pickup object
        pickup = self.find_cell_objects((self.x_coord, self.y_coord), MapObject.domain.objects('pickup'))[0]
        self.inventory = pickup
        # delete pickup object from the domain
        MapObject.domain.delete('pickup', pickup)

    def put_down(self):
        # put down inventory
        if self.reset_queue():
            # no move_to in queue, do directly
            self.place(None)
        else:
            # do after move_to
            self.command(Datagram(self.place, None))

    def place(self, arg):
        # update the pickup object coordinates
        self.inventory.sync((self.x_coord, self.y_coord))
        # place the pickup object back into the domain
        MapObject.domain.object_add('pickup', self.inventory)
        # delete inventory
        self.inventory = None
