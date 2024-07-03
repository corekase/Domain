from .domainobject import DomainObject, Path_To
from .genericobject import GenericObject
from ..utility import sprite_sheet

# named indexes for tiles to map the correct gid
EMPTY, FLOOR, WALL = 0, 1, 2

class AgentObject(DomainObject):
    def __init__(self, position):
        super().__init__()
        self.load_sheet('sprites', 'agent', 'agent_normal.png')
        # speed variable, world pixels per second
        self.speed = 64.0
        self.sync_cell(position)
        # agent memory
        self.destination_object = None

    def process(self):
        if self.destination_object == None:
            if len(self.domain.objects('generic')) > 0:
                # find the nearest item
                path, self.destination_object = DomainObject.domain_manager.find_nearest(
                                                (self.x_coord, self.y_coord),
                                                DomainObject.domain.objects('generic'))
                if path != None:
                    DomainObject.domain.object_remove('generic', self.destination_object)
                    self.command(Path_To((self.destination_object.x_coord, self.destination_object.y_coord)))
        else:
            floor = DomainObject.domain_manager.get_floor(self.destination_object.x_coord)
            # remove reference to old object
            DomainObject.domain.delete('generic', self.destination_object)
            # create a new generic object
            position = DomainObject.domain_manager.random_position_floor(DomainObject.tiles[FLOOR], floor)
            item_object = GenericObject(position)
            item_object.layer = 1
            # track the generic item
            DomainObject.domain.object_add('generic', item_object)
            # reset destination to none
            self.destination_object = None
