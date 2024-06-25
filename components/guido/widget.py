# widget is the base class all gui widgets inherit from
import pygame
from pygame import Rect

white_colour = pygame.Color((255, 255, 255))
light_colour = pygame.Color((192, 192, 192))
medium_colour = pygame.Color((128, 128, 128))
dark_colour = pygame.Color((64, 64, 64))
black_colour = pygame.Color((0, 0, 0))

class Widget:
    IDLE, HOVER = 1, 2

    def __init__(self, id, surface, rect):
        self.id = id
        self.surface = surface
        self.rect = rect
        self.state = None

    def draw_box(self):
        x, y, w, h = self.rect
        if self.state == Widget.HOVER:
            # draw pressed box
            pygame.draw.rect(self.surface, white_colour, self.rect, 0)
        else:
            # draw raised box
            pygame.draw.rect(self.surface, black_colour, self.rect, 0)
