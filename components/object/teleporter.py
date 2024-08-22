from .domainobject import DomainObject, Stall
from ..utility import cut_tile

class Teleporter(DomainObject):
    def __init__(self, graphic, position, destination):
        super().__init__()
        # load either image
        if graphic == 'up':
            self.image = cut_tile(35, 11)
        else:
            self.image = cut_tile(36, 11)
        self.rect = self.image.get_rect()
        # sync position state
        self.sync_cell(position)
        # teleporter destination as a map array coordinate
        self.destination = destination

    def process(self):
        self.command(Stall(None))
