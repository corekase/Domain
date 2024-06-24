from .mapobject import MapObject, Stall
from .utility import image_alpha_resource

# itemobject will have containers items can be in.  If an item is in a container it is removed from the domain
# group.  Once there is a GUI button, then moving the avatar to an item coordinate reveals a "pick up" button
# and the avatar can only have one item in their inventory container.  While they have an inventory they have a
# "drop" button which will update the item coordinate and place it back into the domain group whever the avatar's
# current location is

# dictionary storage: [mapobject][container_name][itemobject]
# each agent has a container dictionary which has itemobject instances. while an item object is in that dictionary
# it isn't in the domain group.  containers as however named just allow addressing to be easily organized

class ItemObject(MapObject):
    def __init__(self):
        super().__init__()
        self.normal_image = image_alpha_resource('sprites', 'item', 'item_generic.png')
        self.overlap_image = self.normal_image
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        # get random starting position
        self.x_coord, self.y_coord = self.find_random_position(MapObject.FLOOR)
        # translate x and y cell coordinates into world pixel coordinates, centered in the position
        self.centre_xpos, self.centre_ypos = self.tile_graphical_centre((self.x_coord, self.y_coord))
        # update position state with the translation
        self.rect_sync((self.centre_xpos, self.centre_ypos))

    def process(self):
        self.command(Stall(None))
