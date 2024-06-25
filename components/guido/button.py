import pygame
from pygame.draw import rect, line
from pygame.locals import MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN
from .widget import Widget
from enum import Enum

State = Enum('State', ['IDLE', 'HOVER', 'ARMED'])

white_colour = pygame.Color((200, 255, 255))
light_colour = pygame.Color((0, 220, 220))
medium_colour = pygame.Color((0, 160, 160))
dark_colour = pygame.Color((0, 80, 80))
black_colour = pygame.Color((0, 0, 0))

# button subclasses widget
class Button(Widget):
    def __init__(self, id, surface, position, text, font_size):
        super().__init__(id, surface, position)
        self.text = text
        self.font_size = font_size
        self.font = pygame.font.Font(pygame.font.get_default_font(), self.font_size)
        self.state = State.IDLE

    def handle_event(self, event):
        if event.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
            # no matching events for button logic
            return False
        collide = self.rect.collidepoint(event.pos)
        if self.state == State.IDLE and collide:
                self.state = State.HOVER
        elif self.state == State.HOVER:
            if (event.type == MOUSEMOTION) and (not collide):
                self.state = State.IDLE
            if (event.type == MOUSEBUTTONDOWN) and collide:
                self.state = State.ARMED
        elif self.state == State.ARMED:
            if (event.type == MOUSEBUTTONUP) and collide:
                self.state = State.HOVER
                # button successfully clicked
                return True
            if (event.type == MOUSEMOTION) and (not collide):
                self.state = State.IDLE
        # did not click
        return False

    def draw(self):
        if self.state == State.IDLE:
            self.draw_frame(light_colour, dark_colour, white_colour, black_colour, medium_colour)
        elif self.state == State.HOVER:
            self.draw_frame(light_colour, dark_colour, white_colour, black_colour, light_colour)
        elif self.state == State.ARMED:
            self.draw_frame(dark_colour, light_colour, black_colour, white_colour, dark_colour)
        text_surface = self.render(self.text)
        x = self.rect[0] + self.centre(self.rect.width, text_surface.get_rect().width) + 1
        y = self.rect[1] + self.centre(self.rect.height, text_surface.get_rect().height) + 1
        self.surface.blit(text_surface, (x, y))

    def draw_frame(self, ul, lr, d_ul, d_lr, background):
        x, y, width, height = self.rect
        # draw background
        rect(self.surface, background, self.rect, 0)
        # draw frame upper and left lines
        line(self.surface, ul, (x, y), (x + width, y))
        line(self.surface, ul, (x, y), (x, y + height))
        # draw frame lower and right lines
        line(self.surface, lr, (x, y + height), (x + width, y + height))
        line(self.surface, lr, (x + width, y), (x + width, y + height))
        # plot upper left dot
        self.surface.set_at((x + 1, y +1), d_ul)
        # plot lower right dot
        self.surface.set_at((x + width - 1, y + height - 1), d_lr)

    def render(self, text):
        return self.font.render(text, True, white_colour)

    def centre(self, bigger, smaller):
        return int((bigger / 2) - (smaller / 2))
