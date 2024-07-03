from .domainobject import DomainObject, Stall
from ..utility import image_alpha_resource

class GenericObject(DomainObject):
    def __init__(self, position):
        super().__init__()
        self.image = image_alpha_resource('sprites', 'item', 'item_generic.png')
        self.rect = self.image.get_rect()
        self.sync_cell(position)

    def process(self):
        self.command(Stall(None))
