from .mapobject import MapObject, Stall
from ..utility import image_alpha_resource

class GenericObject(MapObject):
    def __init__(self):
        super().__init__()
        self.normal_image = image_alpha_resource('sprites', 'item', 'item_generic.png')
        self.overlap_image = self.normal_image
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        # get random starting position
        self.x_coord, self.y_coord = self.find_random_position(MapObject.FLOOR)
        # translate x and y cell coordinates into world pixel coordinates, centered in the position
        self.centre_xpos, self.centre_ypos = self.tile_graphical_centre((self.x_coord, self.y_coord))
        # update position state with the translation
        self.rect_sync((self.centre_xpos, self.centre_ypos))

    def process(self):
        self.command(Stall(None))
