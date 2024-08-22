import os
import pygame
from pygame import Rect
from .gui.guimanager import colours

# these are filled in during the initializer of Main()
font_size = None
font_object = None

# filled in by Main() is the tile sheet tiles are cut out of
tiles = None
tile_size = 32

def cut_tile(tile):
    # cut a tile out of the tile sheet and return it as a surface
    x, y = tile
    surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    surface.blit(tiles, (0, 0), Rect(x * tile_size, y * tile_size, tile_size, tile_size))
    return surface

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
