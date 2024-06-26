from .mapobject import MapObject
from .genericobject import GenericObject
from ..utility import image_alpha_resource

class AgentObject(MapObject):
    def __init__(self):
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
        # get random starting position
        x, y = self.find_random_position(MapObject.FLOOR)
        # translate x and y cell coordinates into world pixel coordinates, centered in the position
        self.centre_xpos, self.centre_ypos = self.tile_graphical_centre((x, y))
        # update position state with the translation
        self.rect_sync((self.centre_xpos, self.centre_ypos))
        # agent memory
        self.destination_object = None

    def process(self):
        if self.destination_object == None:
            if len(self.domain.objects('generic')) > 0:
                # find the nearest item
                path, self.destination_object = self.find_nearest(
                                                (self.x_coord, self.y_coord), self.domain.objects('generic'))
                if path != None:
                    self.domain.object_remove('generic', self.destination_object)
                    self.follow_path(path)
        else:
            # remove reference to old object
            AgentObject.domain.delete('generic', self.destination_object)
            # create a new generic object
            item_object = GenericObject()
            item_object.layer = 1
            # track the generic item
            AgentObject.domain.object_add('generic', item_object)
            # set collision image to normal
            self.image = self.normal_image
            # reset destination to none
            self.destination_object = None
