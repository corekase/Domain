from .domainobject import DomainObject

class GenericObject(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load image
        self.load_sheet('sprites', 'item', 'item_generic.png')
        # sync position state
        self.sync_cell(position)

    def process(self):
        from .domainobject import Stall
        self.command(Stall(None))
