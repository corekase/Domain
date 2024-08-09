from .frame import Frame

class Scrollbar(Frame):
    def __init__(self, surface, id, rect, horizontal):
        # initialize common widget values
        super().__init__(surface, id, rect)
        from pygame import Rect
        # maximum area that can be filled
        self.graphic_rect = Rect(self.rect.left + 4, self.rect.top + 4, self.rect.width - 8, self.rect.height - 8)
        # total size, start and end positions, and bar size within the graphic rect
        self.total_range = self.start_pos = self.bar_size = None
        # whether the scrollbar is horizontal or vertical
        self.horizontal = horizontal
        # state to track if the scrollbar is currently dragging
        self.dragging = False
        # previous mouse position the last time the event was handled
        self.last_mouse_pos = None

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
            x, y = event.pos
            # normalize x and y to graphic drawing area
            x, y = x - self.graphic_rect.x, y - self.graphic_rect.y
            # test bounds for dragging
            escape = False
            if self.horizontal:
                if x < 0 or x > self.graphic_rect.width:
                    escape = True
                else:
                    point = x
            else:
                if y < 0 or y > self.graphic_rect.height:
                    escape = True
                else:
                    point = y
            if escape:
                # outside of bounds, reset
                self.reset_state()
                # signal no change
                return False
            if self.last_mouse_pos != None:
                # there is a previous mouse position, find the change
                mouse_pos = self.graphical_to_total(point)
                # find the difference in mouse movement between handle calls
                mouse_delta = mouse_pos - self.last_mouse_pos
                # calculate bar size and new positions
                new_start_pos = self.start_pos + mouse_delta
                # limit positions
                if new_start_pos < 0:
                    new_start_pos = 0
                if new_start_pos > self.total_range - self.bar_size:
                    new_start_pos = self.total_range - self.bar_size
                # store new positions
                self.start_pos = new_start_pos
                self.last_mouse_pos = mouse_pos
                # signal that there was a change
                return True
            else:
                # if there is no last mouse position make it this one
                self.last_mouse_pos = self.graphical_to_total(point)
                # signal no change
                return False
        if event.type == MOUSEBUTTONUP and self.dragging:
            if event.button == 1:
                # return to default state
                self.reset_state()
                # signal there was a change
                return True
        # signal no changes
        return False

    def reset_state(self):
        from .frame import State
        # reset states to default values
        self.state = State.IDLE
        self.dragging = False
        self.last_mouse_pos = None

    def get(self):
        # return scrollbar start position
        return self.start_pos

    def set(self, total_range, start_pos, bar_size):
        # set scrollbar data
        self.total_range, self.start_pos, self.bar_size = total_range, start_pos, bar_size

    def handle_area(self):
        # calculate where the points are within the graphical area
        start_point = self.total_to_graphical(self.start_pos)
        graphical_size = self.total_to_graphical(self.bar_size)
        from pygame import Rect
        # define a rectangle for the filled area
        if self.horizontal:
            rec = Rect(self.graphic_rect.x + start_point, self.graphic_rect.y, graphical_size, self.graphic_rect.height)
        else:
            rec = Rect(self.graphic_rect.x, self.graphic_rect.y + start_point, self.graphic_rect.width, graphical_size)
        return rec

    def graphical_to_total(self, point):
        return int((point * self.total_range) / self.graphical_range())

    def total_to_graphical(self, point):
        return int((point * self.graphical_range()) / self.total_range)

    def graphical_range(self):
        # return the appropriate range depending on whether the scrollbar is horizontal or vertical
        if self.horizontal:
            return self.graphic_rect.width
        else:
            return self.graphic_rect.height

    def draw(self):
        # draw the frame
        super().draw()
        from components.gui.guimanager import colours
        from pygame.draw import rect
        # fill graphical area to represent the start and end point range
        rect(self.surface, colours['full'], self.handle_area(), 0)
