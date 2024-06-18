from .mapobject import MapObject
from .itemobject import ItemObject
from .utility import image_resource, tile_graphical_centre

class AgentObject(MapObject):
    item_objects = None
    domain = None

    def __init__(self):
        super().__init__()
        # load images for the agents
        self.normal_image = image_resource('sprites', 'agent', 'agent_normal.png')
        self.overlap_image = image_resource('sprites', 'agent', 'agent_overlap.png')
        # set default image for drawing
        self.image = self.normal_image
        # initialize agent rect for movement and drawing
        self.rect = self.image.get_rect()
        # speed variable, world pixels per second
        self.speed = 64.0
        # get random starting position
        x, y = self.find_random_position(MapObject.FLOOR)
        # translate x and y cell coordinates into world pixel coordinates, centered in the position
        self.centre_xpos, self.centre_ypos = tile_graphical_centre(MapObject.map, (x, y))
        # update position state with the translation
        self.rect_sync((self.centre_xpos, self.centre_ypos))
        # agent memory
        self.destination_object = None

    def process(self):
        if self.destination_object != None:
            # remove reference to old object
            AgentObject.domain.remove(self.destination_object)
            # create a new item object
            item_object = ItemObject()
            item_object._layer = 1
            # add it to the item objects list and the domain
            AgentObject.item_objects.append(item_object)
            AgentObject.domain.add(item_object)
            # set collision image to normal
            self.image = self.normal_image
            # reset destination to none
            self.destination_object = None
        elif len(AgentObject.item_objects) > 0:
            # find the nearest item
            path, self.destination_object = self.find_nearest(
                (self.x_coord, self.y_coord), AgentObject.item_objects)
            if path != None:
                AgentObject.item_objects.remove(self.destination_object)
                self.follow_path(path)
