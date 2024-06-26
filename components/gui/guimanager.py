class GuiManager:
    def __init__(self):
        # widgets to be managed
        # todo: add a context variable which indexes into a list of lists of widgets.
        # GUI handle_event and draw_widgets filter by the given context and the context
        # is switched by changing the variable in the application logic
        self.context = None
        self.widgets = dict()

    def switch_context(self, context):
        self.context = context

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
        if not (context in self.widgets.keys()):
            self.widgets[context] = []
        self.widgets[context].append(widget)
