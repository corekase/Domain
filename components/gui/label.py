from .widget import Widget
from ..utility import render_text

class Label(Widget):
    def __init__(self, position, text):
        # text bitmap
        self.text_bitmap = render_text(text)
        # setup rect for the label
        rect = self.text_bitmap.get_rect()
        rect.x, rect.y = position
        # initialize common widget values
        super().__init__('label', rect)

    def handle_event(self, _):
        return False

    def draw(self):
        self.surface.blit(self.text_bitmap, self.rect)
