class GuiManager:
    def __init__(self):
        # widgets to be managed
        # todo: add a context variable which indexes into a list of lists of widgets.
        # GUI handle_event and draw_widgets filter by the given context and the context
        # is switched by changing the variable in the application logic
        self.context = 0
        self.widgets = []

    def switch_context(self, context):
        self.context = context

    def handle_event(self, event):
        # if a widget signals that it had an action return the widget id
        for widget in self.widgets:
            # test widget activation
            if widget.handle_event(event):
                # widget activated, return its id
                return widget.id
        # no widget activated to this event
        return None

    def draw_widgets(self):
        # draw all widgets to their surfaces
        for widget in self.widgets:
            widget.draw()

    def add_widget(self, context, widget):
        # add a widget to the manager
        self.widgets.append(widget)
