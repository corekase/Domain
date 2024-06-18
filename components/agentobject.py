from .mapobject import MapObject, Stall
from .utility import image_resource, tile_graphical_centre

class AgentObject(MapObject):
    item_objects = None
    domain_group = None

    def __init__(self):
        super().__init__()
        # load images for the agents
        self.normal_image = image_resource('sprites', 'agent_normal.png')
        self.overlap_image = image_resource('sprites', 'agent_overlap.png')
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
        self.memory = {}

    def process(self):
        if self.destination_object != None:
            AgentObject.domain_group.remove(self.destination_object)
            self.image = self.normal_image
            self.destination_object = None
        elif len(AgentObject.item_objects) > 0:
            destinations = self.build_list()
            path, self.destination_object = self.find_nearest((self.x_coord, self.y_coord), destinations)
            if path != None:
                AgentObject.item_objects.remove(self.destination_object)
                self.follow_path(path)
            else:
                self.command(Stall(None))
        else:
            self.command(Stall(None))

    def build_list(self):
        destination_list = []
        for item in AgentObject.item_objects:
            destination_list.append([item.x_coord, item.y_coord, item])
        return destination_list
