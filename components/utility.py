import os, pygame
from .gui.widget import colours

# these are filled in during the initializer of Main()
font_size = None
font_object = None

def image_alpha_resource(*names):
    # load, convert with an alpha channel, and return an image surface
    return pygame.image.load(file_resource(*names)).convert_alpha()

def file_resource(*names):
    # return an os-independent filename inside data path
    return os.path.join('data', *names)

def padding(line):
    # text layout helper function
    # return = base + line height + spacer size
    return 1 + (line * font_size) + (line * 2)

def render_text(text):
    # render helper function so same values aren't repeated
    return font_object.render(text, colours['text'], (200, 200, 255))

def centre(bigger, smaller):
    # helper function that returns a centred position
    return int((bigger / 2) - (smaller / 2))
