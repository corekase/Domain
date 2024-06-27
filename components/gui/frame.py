from .widget import Widget
from .widget import gui_colours as colour

class Frame(Widget):
    def __init__(self, surface, rect):
        super().__init__(surface, None, rect)

    def handle_event(self, event):
        return False

    def draw(self):
        self.draw_frame(colour['light'], colour['dark'], colour['full'], colour['none'], colour['medium'])
