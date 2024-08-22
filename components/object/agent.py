from .domainobject import DomainObject, Path
from .generic import Generic
from ..utility import cut_tile

# named indexes for tiles to map the correct gid
FLOOR, WALL = 0, 1

class Agent(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load image
        self.image = cut_tile((50, 67))
        self.rect = self.image.get_rect()
        # world pixels per second
        self.speed = 64.0
        # sync position state
        self.sync_cell(position)
        # agent memory
        self.destination_object = None

    def process(self):
        if self.destination_object == None:
            if len(self.object_manager.objects('generic')) > 0:
                # find the nearest item
                path, self.destination_object = self.domain_manager.find_path(
                    self.coord, self.object_manager.objects('generic'))
                if path != None:
                    self.object_manager.object_remove('generic', self.destination_object)
                    self.command(Path(path))
        else:
            # remove reference to old object
            self.object_manager.delete('generic', self.destination_object)
            # create a new generic object
            position = self.domain_manager.random_position(self.tile_gid[FLOOR], 0, 0,
                                                           self.map_object.width, self.map_object.height)
            item_object = Generic(position)
            item_object.layer = 1
            # track the generic item
            self.object_manager.object_add('generic', item_object)
            # reset destination to none
            self.destination_object = None
