import os, pygame
from pygame import Rect
from .gui.widget import colours

# these are filled in during the initializer of Main()
font_size = None
font_object = None

def sprite_sheet(*names):
    # to-do: a dictionary for each domain object which has a subkey dictionary
    # for each animation sequence and then each of those is a list of animation frames
    image = pygame.image.load(file_resource(*names)).convert_alpha()
    rect = image.get_rect()
    # each image is one frame tall by number of frames to the right
    frames = int(rect.width / rect.height)
    frames_list = []
    for frame in range(frames):
        surface = pygame.Surface((rect.height, rect.height), pygame.SRCALPHA)
        surface.blit(image, (0, 0), Rect(frame * rect.height, 0, rect.height, rect.height))
        frames_list.append(surface)
    # returns list of frames
    return frames_list

def image_alpha(*names):
    # load, convert with an alpha channel, and return an image surface
    return pygame.image.load(file_resource(*names)).convert_alpha()

def file_resource(*names):
    # return an os-independent filename inside data path
    return os.path.join('data', *names)

def padding(line):
    # text layout helper function
    # return = base + line height + spacer size
    return 1 + (line * font_size) + (line * 2)

def render_text(text, highlight=False):
    # render helper function so same values aren't repeated
    if highlight:
        colour = colours['highlight']
    else:
        colour = colours['text']
    # return a bitmap of the chosen colour
    return font_object.render(text, True, colour)

def centre(bigger, smaller):
    # helper function that returns a centred position
    return int((bigger / 2) - (smaller / 2))
