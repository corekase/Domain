# widget is the base class all gui widgets inherit from
from pygame import Rect

class Widget:
    def __init__(self, id, surface, rect):
        self.id = id
        self.surface = surface
        self.rect = Rect(rect)
