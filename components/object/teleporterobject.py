# a cell with a teleporter object may not have any other objects
from .domainobject import DomainObject, Stall
from ..utility import image_alpha_resource

class TeleporterObject(DomainObject):
    def __init__(self, position, destination):
        super().__init__()
        self.normal_image = image_alpha_resource('sprites', 'item', 'teleporter.png')
        self.overlap_image = self.normal_image
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.sync_cell(position)
        self.destination = destination

    def process(self):
        self.command(Stall(None))
