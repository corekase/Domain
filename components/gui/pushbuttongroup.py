from .button import Button

class PushButtonGroup(Button):
    groups = {}

    def __init__(self, surface, id, rect, text, group):
        from .frame import State
        super().__init__(surface, id, rect, text)
        self.group = group
        self.state = State.IDLE
        if group not in PushButtonGroup.groups.keys():
            PushButtonGroup.groups[group] = []
        PushButtonGroup.groups[group].append(self)

    def handle_event(self, event):
        from .frame import State
        # bring in mouse-related events
        from pygame.locals import MOUSEBUTTONDOWN, MOUSEMOTION
        if event.type not in (MOUSEBUTTONDOWN, MOUSEMOTION):
            # no matching events for push button logic
            return False
        # is the mouse position within the button rect
        collision = self.rect.collidepoint(event.pos)
        # manage the state of the push button
        if self.state == State.IDLE and collision:
            self.state = State.HOVER
        elif self.state == State.HOVER:
            if (event.type == MOUSEMOTION) and (not collision):
                self.state = State.IDLE
            if (event.type == MOUSEBUTTONDOWN) and collision:
                if event.button == 1:
                    # push button was clicked
                    self.select()
                    return True
            if (event.type == MOUSEMOTION) and (not collision):
                self.state = State.IDLE
        # push button not clicked
        return False

    def select(self):
        from .frame import State
        # clear all other selected flags in the group and set this one
        for item in PushButtonGroup.groups[self.group]:
            item.state = State.IDLE
        # mark this item as selected
        self.state = State.ARMED

    def draw(self):
        super().draw()
