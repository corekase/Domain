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
        # bring in State from the base Frame
        from .frame import State
        # manage the state of the scrollbar
        if (event.type == MOUSEBUTTONDOWN) and self.handle_area().collidepoint(event.pos):
            if event.button == 1:
                # begin dragging the scrollbar
                self.state = State.HOVER
                self.dragging = True
        if ((event.type == MOUSEMOTION) or (event.type == MOUSEBUTTONDOWN)) and self.dragging:
            # adjust postion
            x, y = event.pos
            # normalize x and y to graphic drawing area
            x, y = x - self.graphic_rect.x, y - self.graphic_rect.y
            size = self.total_range / self.graphical_range()



            if self.horizontal:
                new_coord = int(x * size)
            else:
                new_coord = int(y * size)

            # convert mouse coordinate to total range coordinate

            # get the differences of the mouse range coordinate and start_pos and make that new_pos


            # if new_pos + area bar size > bar end, then new start_pos = bar end - area bar size

            bar_size = self.end_pos - self.start_pos
            new_pos = new_coord + bar_size
            if new_pos > self.total_range:
                new_pos = self.total_range - bar_size

            # store new positions
            self.start_pos = new_coord
            # self.end_pos = None
            # self.total_range = None

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

    def graphical_range(self):
        # return the appropriate range depending on whether the scrollbar is horizontal or vertical
        if self.horizontal:
            return self.graphic_rect.width
        else:
            return self.graphic_rect.height

    def handle_area(self):
        # calculate percentages from the start and end positions
        start_percent = (self.start_pos * 100) / self.total_range
        end_percent = (self.end_pos * 100) / self.total_range
        # calculate where the percentages are within the graphical area
        graphical_range = self.graphical_range()
        start_point = int((start_percent * graphical_range) / 100)
        end_point = int((end_percent * graphical_range) / 100)
        from pygame import Rect
        # define a rectangle for the filled area
        if self.horizontal:
            rec = Rect(self.graphic_rect.x + start_point, self.graphic_rect.y, end_point, self.graphic_rect.height)
        else:
            rec = Rect(self.graphic_rect.x, self.graphic_rect.y + start_point, self.graphic_rect.width, end_point)
        return rec

    def draw(self):
        # draw the frame
        super().draw()
        from components.gui.guimanager import colours
        from pygame.draw import rect
        # fill graphical area to represent the start and end point range
        rect(self.surface, colours['full'], self.handle_area(), 0)
