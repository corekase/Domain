from .domainobject import DomainObject, Stall

class Teleporter(DomainObject):
    def __init__(self, graphic, position, destination):
        super().__init__()
        # load either image
        if graphic == 'up':
            self.load_tiles([(35, 11)])
        else:
            self.load_tiles([(36, 11)])
        # sync position state
        self.sync_cell(position)
        # teleporter destination as a map array coordinate
        self.destination = destination

    def process(self):
        self.command(Stall(None))
