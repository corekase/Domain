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
                    self.gui.switch_context(0)
            else:
                # no pickups at location and no inventory, disable both contexts
                self.gui.switch_context(None)
        else:
            # enable drop button
            self.gui_switch_context(1)

    def move_to(self, position):
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
        pass

    def put_down(self):
        # put down does the same as move_to, if there is a move then datagram the put down after
        # the one move command completes
        pass
