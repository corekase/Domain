from .domainobject import DomainObject, Stall

class Pickup(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load tile image
        self.load_tiles([(43, 41)])
        # sync position state
        self.sync_cell(position)

    def process(self):
        self.command(Stall(None))
