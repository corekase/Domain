from .mapobject import MapObject, Stall
from .util import image_resource, tile_graphical_centre

class Agent(MapObject):
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
        self.memory = {}

    def process(self):
        while True:
            # find a random position with a floor tile
            destination = self.find_random_position(MapObject.FLOOR)
            if self.x_coord != destination[0] or self.y_coord != destination[1]:
                break
        # find and add a path to the command queue from the agents current position to that destination
        path = self.find_path((self.x_coord, self.y_coord), destination)
        if path != None:
            self.follow_path(path)
        else:
            # not a valid path, suspend the agent.
            self.queue(Stall(None))
