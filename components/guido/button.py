from pygame.locals import MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN
from .widget import Widget
from enum import Enum

State = Enum('State', ['IDLE', 'HOVER', 'ARMED'])

# button subclasses widget
class Button(Widget):
    def __init__(self, id, surface, position, text):
        super().__init__(id, surface, position)
        self.text = text
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
                self.state = State.IDLE
                # button successfully clicked
                return True
            if (event.type == MOUSEMOTION) and (not collide):
                self.state = State.IDLE
        # did not click
        return False

    def draw(self):
        if self.state == State.IDLE:
            self.draw_box('idle')
        elif self.state == State.HOVER:
            self.draw_box('hover')
        elif self.state == State.ARMED:
            self.draw_box('armed')
