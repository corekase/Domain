from .button import Button

class PushButtonGroup(Button):
    groups = {}

    def __init__(self, surface, id, rect, text, group, selected):
        super().__init__(surface, id, rect, text)
        self.group = group
        self.selected = selected
        if group not in PushButtonGroup.groups.keys():
            PushButtonGroup.groups[group] = []
        PushButtonGroup.groups[group].append(self)

    def handle_event(self, event):
        # bring in mouse-related events
        from pygame.locals import MOUSEBUTTONDOWN
        if event.type != MOUSEBUTTONDOWN:
            # no matching events for button logic
            return False
        # is the mouse position within the button rect
        collision = self.rect.collidepoint(event.pos)
        # manage the state of the button
        if (event.type == MOUSEBUTTONDOWN) and collision:
            if event.button == 1:
                self.select()
                return True
        # button not clicked
        return False

    def select(self):
        # clear all other selected flags in the group and set this one
        for item in PushButtonGroup.groups[self.group]:
            item.selected = False
        # mark this item as selected
        self.selected = True

    def draw(self):
        from .frame import State
        if self.selected:
            self.state = State.ARMED
        else:
            self.state = State.IDLE
        super().draw()
