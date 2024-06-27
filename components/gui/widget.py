# widget is the base class all gui widgets inherit from
from pygame import Rect
from pygame.draw import rect, line

gui_colours = dict()
gui_colours['full'] = (255, 255, 255)
gui_colours['light'] = (0, 200, 200)
gui_colours['medium'] = (0, 140, 140)
gui_colours['dark'] = (0, 80, 80)
gui_colours['none'] = (0, 0, 0)

class Widget:
    def __init__(self, surface, id, rect):
        # surface to draw the widget on
        self.surface = surface
        # identifier for widget, can be any kind like int or string
        self.id = id
        # rect for widget position and size on the surface
        self.rect = Rect(rect)

    def handle_event(self, event):
        # implement in subclasses
        pass

    def draw(self):
        # implement in subclasses
        pass

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
