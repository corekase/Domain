from .domainobject import DomainObject, Stall
from ..utility import image_alpha_resource

class PickupObject(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load image
        self.load_sheet('sprites', 'item', 'pickup.png')
        # sync position state
        self.sync_cell(position)

    def process(self):
        self.command(Stall(None))
