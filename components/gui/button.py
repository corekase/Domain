import pygame
from enum import Enum
from pygame.locals import MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN
from .widget import Widget
from .widget import gui_colours as colour
from ..utility import render, centre

State = Enum('State', ['IDLE', 'HOVER', 'ARMED'])

class Button(Widget):
    def __init__(self, surface, id, rect, text):
        # initialize common widget values
        super().__init__(surface, id, rect)
        # text bitmap
        self.text_bitmap = render(text)
        # get centred dimensions for both x and y ranges
        text_x = self.rect.x + centre(self.rect.width, self.text_bitmap.get_rect().width)
        text_y = self.rect.y + centre(self.rect.height, self.text_bitmap.get_rect().height)
        # store the position for later blitting
        self.position = text_x, text_y
        # button state
        self.state = State.IDLE

    def handle_event(self, event):
        if not (event.type in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN)):
            # no matching events for button logic
            return False
        # is the mouse position within the button rect
        collision = self.rect.collidepoint(event.pos)
        # manage the state of the button
        if self.state == State.IDLE and collision:
            self.state = State.HOVER
        elif self.state == State.HOVER:
            if (event.type == MOUSEMOTION) and (not collision):
                self.state = State.IDLE
            if (event.type == MOUSEBUTTONDOWN) and collision:
                if event.button == 1:
                    self.state = State.ARMED
        elif self.state == State.ARMED:
            if (event.type == MOUSEBUTTONUP) and collision:
                if event.button == 1:
                    # button clicked
                    self.state = State.HOVER
                    return True
            if (event.type == MOUSEMOTION) and (not collision):
                self.state = State.IDLE
        # button not clicked
        return False

    def draw(self):
        # draw the button frame
        if self.state == State.IDLE:
            self.draw_frame(colour['light'], colour['dark'], colour['full'], colour['none'], colour['medium'])
        elif self.state == State.HOVER:
            self.draw_frame(colour['light'], colour['dark'], colour['full'], colour['none'], colour['light'])
        elif self.state == State.ARMED:
            self.draw_frame(colour['none'], colour['light'], colour['none'], colour['full'], colour['dark'])
        # draw the button text
        self.surface.blit(self.text_bitmap, self.position)
