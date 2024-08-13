from .domainobject import DomainObject
from .domainobject import Stall

class Pickup(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load image
        self.load_sheet('sprites', 'item', 'pickups', 'pickup.png')
        # sync position state
        self.sync_cell(position)

    def process(self):
        self.command(Stall(None))
