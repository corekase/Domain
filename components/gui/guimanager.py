import pygame
from pygame import Rect
# named colour values, in one location to change everywhere
colours = {'full': (255, 255, 255), 'light': (0, 200, 200), 'medium': (0, 150, 150), 'dark': (0, 100, 100), 'none': (0, 0, 0),
           'text': (255, 255, 255), 'highlight': (238, 230, 0), 'background': (0, 60, 60)}

class GuiManager:
    def __init__(self, surface):
        # surface to draw the widget to
        self.surface = surface
        # widgets to be managed: key:value -> group_name:list_of_widgets
        self.widgets = {}
        # global widgets which are always shown and processed
        self.widgets['global'] = []
        # which key group to show
        self.context = None
        # lock to this context
        self.locked_context = None
        # list of bitmaps overwritten by gui objects
        self.bitmaps = []

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
        widgets = self.widgets['global'] + self.widgets.get(self.context, [])
        for widget in widgets:
            # test widget activation
            if widget.handle_event(event):
                # widget activated, return its id
                return widget.id
        # no widget activated to this event
        return None

    def draw_widgets(self):
        # draw all widgets to their surfaces
        widgets = self.widgets['global'] + self.widgets.get(self.context, [])
        # clear previous bitmaps
        self.bitmaps = []
        for widget in widgets:
            # create a surface of the same size as the widget
            bitmap = pygame.Surface((widget.rect.width, widget.rect.height))
            # save the bitmap that is under the widget rect
            bitmap.blit(self.surface, (0, 0), widget.rect)
            # each list item is a tuple of the bitmap and its rect
            self.bitmaps += [(bitmap, widget.rect)]
            # draw the widget
            widget.draw()

    def undraw_widgets(self):
        # restore the bitmaps that were under each gui object drawn
        for bitmap, rect in self.bitmaps:
            self.surface.blit(bitmap, rect)

    def add_widget(self, context, widget):
        # add a widget to the manager
        if context not in self.widgets.keys():
            self.widgets[context] = []
        # give the widget a reference to the screen
        widget.surface = self.surface
        # append the widget to the context
        self.widgets[context].append(widget)
