# a cell with a teleporter object may not have any other objects
from .domainobject import DomainObject, Stall
from ..utility import image_alpha_resource

class TeleporterObject(DomainObject):
    def __init__(self, graphic, position, destination):
        super().__init__()
        if graphic == 'up':
            self.load_sheet('sprites', 'item', 'teleporter_up.png')
        else:
            self.load_sheet('sprites', 'item', 'teleporter_down.png')
        self.sync_cell(position)
        self.destination = destination

    def process(self):
        self.command(Stall(None))
