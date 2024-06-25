class GuiManager:
    def __init__(self):
        # widgets to be managed
        # todo: add a context variable which indexes into a list of lists of widgets.
        # GUI handle_event and draw_widgets filter by the given context and the context
        # is switched by changing the variable in the application logic
        self.context = 0
        self.widgets = []

    def handle_event(self, event):
        # if a widget signals that it had an action return the widget id
        for widget in self.widgets:
            signal = widget.handle_event(event)
            if signal:
                return widget.id
        return None

    def draw_widgets(self):
        for widget in self.widgets:
            widget.draw()

    def add_widget(self, widget):
        self.widgets.append(widget)
