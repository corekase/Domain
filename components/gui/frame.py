from enum import Enum
from pygame.draw import rect, line
from .widget import Widget
from .widget import colours

State = Enum('State', ['IDLE', 'HOVER', 'ARMED'])

class Frame(Widget):
    def __init__(self, surface, id, rect):
        super().__init__(surface, id, rect)
        self.state = State.IDLE

    def handle_event(self, _):
        return False

    def draw(self):
        if self.state == State.IDLE:
            self.draw_frame(colours['light'], colours['dark'], colours['full'], colours['none'], colours['medium'])
        elif self.state == State.HOVER:
            self.draw_frame(colours['light'], colours['dark'], colours['full'], colours['none'], colours['light'])
        elif self.state == State.ARMED:
            self.draw_frame(colours['none'], colours['light'], colours['none'], colours['full'], colours['dark'])

    def draw_frame(self, ul, lr, ul_d, lr_d, background):
        # ul, lr = upper and left, lower and right lines
        # ul_d, lr_d = upper-left dot, lower-right dot
        # get positions and sizes
        x, y, width, height = self.rect
        # lock surface for drawing
        self.surface.lock()
        # draw background
        rect(self.surface, background, self.rect, 0)
        # draw frame upper and left lines
        line(self.surface, ul, (x, y), (x + width, y))
        line(self.surface, ul, (x, y), (x, y + height))
        # draw frame lower and right lines
        line(self.surface, lr, (x, y + height), (x + width, y + height))
        line(self.surface, lr, (x + width, y), (x + width, y + height))
        # plot upper left dot
        self.surface.set_at((x + 1, y +1), ul_d)
        # plot lower right dot
        self.surface.set_at((x + width - 1, y + height - 1), lr_d)
        # unlock surface
        self.surface.unlock()
