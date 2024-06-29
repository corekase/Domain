from .domainobject import DomainObject
from .genericobject import GenericObject
from ..utility import image_alpha_resource

class AgentObject(DomainObject):
    def __init__(self, floor, position):
        super().__init__()
        # load images for the agents
        self.normal_image = image_alpha_resource('sprites', 'agent', 'agent_normal.png')
        self.overlap_image = image_alpha_resource('sprites', 'agent', 'agent_overlap.png')
        # set default image for drawing
        self.image = self.normal_image
        # initialize agent rect for movement and drawing
        self.rect = self.image.get_rect()
        # speed variable, world pixels per second
        self.speed = 64.0
        self.floor = floor
        self.sync_cell(position)
        # agent memory
        self.destination_object = None

    def process(self):
        if self.destination_object == None:
            if len(self.domain.objects('generic')) > 0:
                # find the nearest item
                path, self.destination_object = self.find_nearest(
                                                (self.x_coord, self.y_coord),
                                                DomainObject.domain.objects('generic'))
                if path != None:
                    DomainObject.domain.object_remove('generic', self.destination_object)
                    self.follow_path(path)
        else:
            floor = self.destination_object.floor
            # remove reference to old object
            DomainObject.domain.delete('generic', self.destination_object)
            # create a new generic object
            position = self.map_manager.find_random_position_floor(DomainObject.tiles[0], floor, 30)
            item_object = GenericObject(floor, position)
            item_object.layer = 1
            # track the generic item
            DomainObject.domain.object_add('generic', item_object)
            # set collision image to normal
            self.image = self.normal_image
            # reset destination to none
            self.destination_object = None
