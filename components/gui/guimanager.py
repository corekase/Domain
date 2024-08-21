# named colour values, in one location to change everywhere
colours = {'full': (255, 255, 255), 'light': (202, 126, 59), 'medium': (158, 89, 0), 'dark': (46, 13, 0), 'none': (0, 0, 0),
           'text': (255, 255, 255), 'highlight': (238, 230, 0), 'background': (82, 31, 0)}

class GuiManager:
    def __init__(self):
        # widgets to be managed: key:value -> group_name:list_of_widgets
        self.widgets = {}
        # which key group to show
        self.context = None
        # lock to this context
        self.locked_context = None

    def switch_context(self, context):
        # if locked_context isn't None then ignore the switch_context call
        if self.locked_context == None:
            # set which key group is active
            self.context = context

    def lock_context(self, lock_context):
        # call with a context to lock to or None to clear
        self.locked_context = lock_context
        self.context = lock_context

    def handle_event(self, event):
        # if a widget signals that it had an action return the widget id
        if self.context != None:
            for widget in self.widgets[self.context]:
                # test widget activation
                if widget.handle_event(event):
                    # widget activated, return its id
                    return widget.id
        # no widget activated to this event
        return None

    def draw_widgets(self):
        # draw all widgets to their surfaces
        if self.context != None:
            for widget in self.widgets[self.context]:
                widget.draw()

    def add_widget(self, context, widget):
        # add a widget to the manager
        if context not in self.widgets.keys():
            self.widgets[context] = []
        self.widgets[context].append(widget)
