import os, pygame
from .gui.widget import gui_colours as colour

def image_alpha_resource(*names):
    # load, convert with an alpha channel, and return an image surface
    return pygame.image.load(file_resource(*names)).convert_alpha()

def file_resource(*names):
    # return an os-independent filename inside data path
    return os.path.join('data', *names)

def padding(line, size):
    # text layout helper function
    # return = base + line height + spacer size
    return 1 + (line * size) + (line * 1)

def render(font, text):
    # render helper function so same values aren't repeated
    return font.render(text, colour['full'], (200, 200, 255))

def centre(bigger, smaller):
    # helper function that returns a centred position
    return int((bigger / 2) - (smaller / 2))
