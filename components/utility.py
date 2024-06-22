import os, pygame

def tile_graphical_centre(data_source, location):
    # given a tile x and y coordinate return the graphical x and y center point
    x_width, y_height = data_source.tilewidth, data_source.tileheight
    x_centre, y_centre = int(x_width / 2), int(y_height / 2)
    return (location[0] * x_width) + x_centre, (location[1] * y_height) + y_centre

def image_resource(*names):
    # load and return an image surface
    return pygame.image.load(file_resource(*names)).convert_alpha()

def file_resource(*names):
    # return an os-independent filename inside data path
    return os.path.join('data', *names)
