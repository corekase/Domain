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
        # disable all buttons
        pass
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
            # reset_queue will leave the first move_to command if any are in the queue
            # after that left move_to put in a datagram so that when the queue gets to
            # the datagram command the mapobject coordinates will then be current
            self.command(Datagram(self.path_to, position))

    def path_to(self, new_position):
        # from current position go to new_position
        self.command(Path_To(new_position))

    def pick_up(self):
        pickup = self.find_cell_objects((self.x_coord, self.y_coord), MapObject.domain.objects('pickup'))[0]
        self.inventory = pickup
        MapObject.domain.delete('pickup', pickup)

    def put_down(self):
        if self.reset_queue():
            self.place(None)
        else:
            self.command(Datagram(self.place, None))

    def place(self, arg):
        self.inventory.centre_xpos, self.inventory.centre_ypos = self.tile_graphical_centre((self.x_coord, self.y_coord))
        self.inventory.rect_sync((self.inventory.centre_xpos, self.inventory.centre_ypos))

        MapObject.domain.object_add('pickup', self.inventory)
        self.inventory = None
