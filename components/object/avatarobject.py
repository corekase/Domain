from .mapobject import MapObject
from .mapobject import Path_To
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

    def process(self):
        pass

    def move_to(self, position):
        x_cell, y_cell = position
        self.command(Path_To((x_cell, y_cell)))

    def pick_up(self):
        pass

    def put_down(self):
        pass
