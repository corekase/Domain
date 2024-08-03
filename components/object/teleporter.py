# a cell with a teleporter object may not have any other objects
from .domainobject import DomainObject

class Teleporter(DomainObject):
    def __init__(self, graphic, position, destination):
        super().__init__()
        # load either image
        if graphic == 'up':
            self.load_sheet('sprites', 'teleporter', 'teleporter_up.png')
        else:
            self.load_sheet('sprites', 'teleporter', 'teleporter_down.png')
        # sync position state
        self.sync_cell(position)
        # teleporter destination as a map array coordinate
        self.destination = destination

    def process(self):
        from .domainobject import Stall
        self.command(Stall(None))
