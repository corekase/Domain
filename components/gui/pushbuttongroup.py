from .button import Button

class PushButtonGroup(Button):
    groups = {}

    def __init__(self, surface, id, rect, text, group):
        super().__init__(surface, id, rect, text)
        self.group = group
        if group not in PushButtonGroup.groups.keys():
            PushButtonGroup.groups[group] = []
        PushButtonGroup.groups[group].append(self)

    def handle_event(self, event):
        from .frame import State
        # bring in mouse-related events
        from pygame.locals import MOUSEMOTION, MOUSEBUTTONDOWN
        if event.type not in (MOUSEMOTION, MOUSEBUTTONDOWN):
            # no matching events for push button logic
            return False
        # is the mouse position within the push button rect
        collision = self.rect.collidepoint(event.pos)
        # manage the state of the push button
        if self.state == State.IDLE and collision:
            self.state = State.HOVER
        if self.state == State.HOVER:
            if (event.type == MOUSEMOTION) and (not collision):
                self.state = State.IDLE
            if (event.type == MOUSEBUTTONDOWN) and collision:
                if event.button == 1:
                    # push button was clicked
                    self.select()
                    return True
        # push button not clicked
        return False

    def select(self):
        from .frame import State
        # clear all other armed states in the group and set this one as armed
        for item in PushButtonGroup.groups[self.group]:
            item.state = State.IDLE
        # mark this item armed
        self.state = State.ARMED

    def draw(self):
        super().draw()
