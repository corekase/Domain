from pygame.locals import MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN
from .widget import Widget
from enum import Enum

# button subclasses widget
class Button(Widget):
    def __init__(self, id, surface, position, text):
        super().__init__(id, surface, position)
        self.text = text
        self.state = Widget.IDLE

    def handle_event(self, event):
        if event.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
            # no matching events for button logic
            return False
        collide = self.rect.collidepoint(event.pos)
        if self.state == Widget.IDLE and collide:
                self.state = Widget.HOVER
        elif self.state == Widget.HOVER:
            if (event.type == MOUSEBUTTONUP) and collide:
                self.state = Widget.IDLE
                # button successfully clicked
                return True
            if (event.type == MOUSEMOTION) and (not collide):
                self.state = Widget.IDLE
        # did not click
        return False

    def draw(self):
        self.draw_box()
