# a cell with a teleporter object may not have any other objects
from .domainobject import DomainObject, Stall
from ..utility import image_alpha_resource

class TeleporterObject(DomainObject):
    def __init__(self, dest_floor, graphic, position, destination):
        super().__init__()
        # destination floor of the teleport, used to adjust the viewport when
        # switching floors
        self.dest_floor = dest_floor
        if graphic == 'up':
            self.normal_image = image_alpha_resource('sprites', 'item', 'teleporter_up.png')
        else:
            self.normal_image = image_alpha_resource('sprites', 'item', 'teleporter_down.png')
        self.overlap_image = self.normal_image
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.sync_cell(position)
        self.destination = destination

    def process(self):
        self.command(Stall(None))
