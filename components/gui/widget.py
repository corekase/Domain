# widget is the base class all gui widgets inherit from
class Widget:
    def __init__(self, surface, id, rect):
        from pygame import Rect
        # surface to draw the widget on
        self.surface = surface
        # identifier for widget, can be any kind like int or string
        self.id = id
        # rect for widget position and size on the surface
        self.rect = Rect(rect)

    def handle_event(self, _):
        # implement in subclasses
        pass

    def draw(self):
        # implement in subclasses
        pass
