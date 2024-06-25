# widget is the base class all gui widgets inherit from
import pygame
from pygame import Rect
from pygame.draw import rect, line

white_colour = pygame.Color((200, 255, 255))
light_colour = pygame.Color((0, 220, 220))
medium_colour = pygame.Color((0, 160, 160))
dark_colour = pygame.Color((0, 80, 80))
black_colour = pygame.Color((0, 0, 0))

class Widget:
    def __init__(self, id, surface, rect):
        self.id = id
        self.surface = surface
        self.rect = Rect(rect)

    def draw_box(self, state):
        x, y, w, h = self.rect
        if state == 'hover':
            # draw hover box
            rect(self.surface, light_colour, self.rect, 0)
        elif state == 'idle':
            # draw normal box
            rect(self.surface, medium_colour, self.rect, 0)
        elif state == 'armed':
            # draw armed box
            rect(self.surface, dark_colour, self.rect, 0)
