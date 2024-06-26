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
        position = self.find_random_position(MapObject.FLOOR)
        self.sync_cell(position)

    def process(self):
        self.command(Stall(None))
