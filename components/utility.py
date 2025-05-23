import os
import pygame
from pygame import Rect
from components.gui.widget import colours

# these are filled in during the initializer of Main()
font_size = None
font_object = None
screen = None
# filled in by Main() is the tile sheet tiles are cut out of
tiles = None
# graphic size of the tile, squared
tile_size = 32
# dictionary to cache images so one surface for one tile position and reused on later calls
tile_images = {}

def cut(surface, rect, flags = 0):
    bitmap = pygame.Surface((rect.width, rect.height), flags)
    bitmap.blit(surface, (0, 0), rect)
    return bitmap

def cut_tile(tile):
    # if the tile is cached return that otherwise create the graphic image and cache it
    if tile not in tile_images.keys():
        x, y = tile
        surface = cut(tiles, Rect(x * tile_size, y * tile_size, tile_size, tile_size), pygame.SRCALPHA)
        tile_images[tile] = surface
    return tile_images[tile]

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
