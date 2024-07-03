from .domainobject import DomainObject, Stall
from ..utility import image_alpha_resource

class GenericObject(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load image
        self.load_sheet('sprites', 'item', 'item_generic.png')
        # sync position state
        self.sync_cell(position)

    def process(self):
        self.command(Stall(None))
