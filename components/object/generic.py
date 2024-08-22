from .domainobject import DomainObject, Stall

class Generic(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load tile image
        self.load_tiles([(51, 49)])
        # sync position state
        self.sync_cell(position)

    def process(self):
        self.command(Stall(None))
