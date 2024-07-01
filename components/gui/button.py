from pygame.locals import MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN
from ..utility import render_text, centre
from .frame import State, Frame

class Button(Frame):
    def __init__(self, surface, id, rect, text):
        # initialize common widget values
        super().__init__(surface, id, rect)
        # button state
        self.state = State.IDLE
        # text bitmap
        self.text_bitmap = render_text(text)
        # get centred dimensions for both x and y ranges
        text_x = self.rect.x + centre(self.rect.width, self.text_bitmap.get_rect().width)
        text_y = self.rect.y + centre(self.rect.height, self.text_bitmap.get_rect().height)
        # store the position for later blitting
        self.position = text_x, text_y

    def handle_event(self, event):
        if not (event.type in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN)):
            # no matching events for button logic
            return False
        # is the mouse position within the button rect
        collision = self.rect.collidepoint(event.pos)
        # manage the state of the button
        if self.state == State.IDLE and collision:
            self.state = State.HOVER
        elif self.state == State.HOVER:
            if (event.type == MOUSEMOTION) and (not collision):
                self.state = State.IDLE
            if (event.type == MOUSEBUTTONDOWN) and collision:
                if event.button == 1:
                    self.state = State.ARMED
        elif self.state == State.ARMED:
            if (event.type == MOUSEBUTTONUP) and collision:
                if event.button == 1:
                    # button clicked
                    self.state = State.HOVER
                    return True
            if (event.type == MOUSEMOTION) and (not collision):
                self.state = State.IDLE
        # button not clicked
        return False

    def draw(self):
        # draw the button frame
        super().draw()
        # draw the button text
        self.surface.blit(self.text_bitmap, self.position)
