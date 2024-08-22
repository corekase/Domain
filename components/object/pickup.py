from .domainobject import DomainObject, Stall
from ..utility import cut_tile

class Pickup(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load image
        self.image = cut_tile((43, 41))
        self.rect = self.image.get_rect()
        # sync position state
        self.sync_cell(position)

    def process(self):
        self.command(Stall(None))
