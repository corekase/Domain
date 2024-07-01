from .domainobject import DomainObject, Stall
from ..utility import image_alpha_resource

class PickupObject(DomainObject):
    def __init__(self, position):
        super().__init__()
        self.normal_image = image_alpha_resource('sprites', 'item', 'pickup.png')
        self.overlap_image = self.normal_image
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.sync_cell(position)

    def process(self):
        self.command(Stall(None))
