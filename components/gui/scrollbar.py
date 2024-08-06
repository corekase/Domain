from .frame import Frame

class Scrollbar(Frame):
    def __init__(self, surface, id, rect, horizontal):
        # initialize common widget values
        super().__init__(surface, id, rect)
        from pygame import Rect
        # maximum area that can be filled
        self.graphic_rect = Rect(self.rect.left + 4, self.rect.top + 4, self.rect.width - 8, self.rect.height - 8)
        # total size, and start and end positions within that
        self.total_range = self.start_pos = self.end_pos = None
        # whether the scrollbar is horizontal or vertical
        self.horizontal = horizontal
        # state to track if the scrollbar is currently dragging
        self.dragging = False

    def handle_event(self, event):
        # bring in mouse-related events
        from pygame.locals import MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN
        if event.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
            # no matching events for scrollbar logic
            return False
        # is the mouse position within the scrollbar rect
        collision = self.rect.collidepoint(event.pos)
        # bring in State from the base Frame
        from .frame import State
        # manage the state of the scrollbar
        if (event.type == MOUSEBUTTONDOWN) and collision:
            if event.button == 1:
                # begin dragging the scrollbar
                self.state = State.HOVER
                self.dragging = True
        if ((event.type == MOUSEMOTION) or (event.type == MOUSEBUTTONDOWN)) and self.dragging:
            # adjust postion
            x, y = event.pos
            if self.horizontal:
                graphical_range = self.graphic_rect.width
            else:
                graphical_range = self.graphic_rect.height
            size = self.total_range / graphical_range
            if self.horizontal:
                new_coord = int(x * size)
            else:
                new_coord = int(y * size)
            self.start_pos = new_coord
            # signal that there was a change
            return True
        if event.type == MOUSEBUTTONUP and self.dragging:
            if event.button == 1:
                # mouse button released, stop dragging the scrollbar
                self.state = State.IDLE
                self.dragging = False
        # no changes
        return False

    def set(self, total_range, start_pos, end_pos):
        # set scrollbar data
        self.total_range, self.start_pos, self.end_pos = total_range, start_pos, end_pos

    def get(self):
        # return scrollbar start position
        return self.start_pos

    def draw(self):
        # draw the frame
        super().draw()
        # calculate percentages from the start and end positions
        start_percent = (self.start_pos * 100) / self.total_range
        end_percent = (self.end_pos * 100) / self.total_range
        if self.horizontal:
            graphical_range = self.graphic_rect.width
        else:
            graphical_range = self.graphic_rect.height
        # calculate where the percentages are within the graphical area
        start_point = int((start_percent * graphical_range) / 100)
        end_point = int((end_percent * graphical_range) / 100)
        from pygame import Rect
        # define a rectangle for the filled area
        if self.horizontal:
            rec = Rect(self.graphic_rect.x + start_point, self.graphic_rect.y, end_point, self.graphic_rect.height)
        else:
            rec = Rect(self.graphic_rect.x, self.graphic_rect.y + start_point, self.graphic_rect.width, end_point)
        from components.gui.guimanager import colours
        from pygame.draw import rect
        # lock surface and draw the rectangle
        self.surface.lock()
        rect(self.surface, colours['full'], rec, 0)
        self.surface.unlock()
