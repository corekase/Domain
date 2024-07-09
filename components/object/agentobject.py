from .domainobject import DomainObject

# named indexes for tiles to map the correct gid
EMPTY, FLOOR, WALL = 0, 1, 2

class AgentObject(DomainObject):
    def __init__(self, position):
        super().__init__()
        # load image
        self.load_sheet('sprites', 'agent', 'agent.png')
        # frame time
        self.interval = 0.2
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
                path, self.destination_object = self.domain_manager.find_nearest(
                                                (self.x_coord, self.y_coord),
                                                self.object_manager.objects('generic'))
                if path != None:
                    from .domainobject import Path_To
                    self.object_manager.object_remove('generic', self.destination_object)
                    self.command(Path_To((self.destination_object.x_coord, self.destination_object.y_coord)))
        else:
            from .genericobject import GenericObject
            floor = self.domain_manager.get_floor(self.destination_object.x_coord)
            # remove reference to old object
            self.object_manager.delete('generic', self.destination_object)
            # create a new generic object
            position = self.domain_manager.random_position_floor(self.tile_gid[FLOOR], floor)
            item_object = GenericObject(position)
            item_object.layer = 1
            # track the generic item
            self.object_manager.object_add('generic', item_object)
            # reset destination to none
            self.destination_object = None
