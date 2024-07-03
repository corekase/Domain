# a cell with a teleporter object may not have any other objects
from .domainobject import DomainObject, Stall

class TeleporterObject(DomainObject):
    def __init__(self, graphic, position, destination):
        super().__init__()
        # load either image
        if graphic == 'up':
            self.load_sheet('sprites', 'item', 'teleporter_up.png')
        else:
            self.load_sheet('sprites', 'item', 'teleporter_down.png')
        # sync position state
        self.sync_cell(position)
        # teleporter destination in cell coordinates
        self.destination = destination

    def process(self):
        self.command(Stall(None))
