# the gui manager will handle zones and widgets.  the first widget
# will be a button

class GuiManager:
    def __init__(self):
        # all widgets to be managed
        self.widgets = []

    def handle_event(self, event):
        # return only confirmed events like valid click on button
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
