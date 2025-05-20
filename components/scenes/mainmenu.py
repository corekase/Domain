import pygame
from pygame import Rect, QUIT
from pygame.locals import MOUSEMOTION, KEYDOWN, K_ESCAPE
from components.gui.guimanager import GuiManager
from components.gui.frame import Frame
from components.gui.button import Button
from components.gui.label import Label
from components.utility import image_alpha, cut, file_resource, centre

class MainMenu:
    def __init__(self, screen):
        # main window surface
        self.screen = screen
        width = 200
        height = 80
        x = centre(self.screen.get_rect().width, width)
        y = centre(self.screen.get_rect().height, height)
        frame = Rect(x, y, width, height)
        self.gui_manager = GuiManager(self.screen)
        self.gui_manager.add_widget('menu', Frame('frame', frame))
        label = Label((0, 0), 'Main Menu')
        label.rect.x = frame.x + centre(frame.width, label.rect.width)
        label.rect.y = y + 2
        self.gui_manager.add_widget('menu', label)
        self.gui_manager.add_widget('menu', Button('play',
                        Rect(x + 10, y + 25, width - 20, 20), 'Play'))
        self.gui_manager.add_widget('menu', Button('exit',
                        Rect(x + 10, y + 50, width - 20, 20), 'Exit'))
        self.gui_manager.switch_context('menu')
        self.cursor_image = image_alpha('cursors', 'Icons8_cursor.png')
        self.mouse_position = pygame.mouse.get_pos()
        # set a background image
        self.screen.blit(pygame.image.load(file_resource('images', 'watercolor-green-wallpaper-modified.jpg')).convert(), (0, 0))

    def run(self):
        fps = 0
        clock = pygame.time.Clock()
        while True:
            signal = self.handle_events()
            if signal != None:
                return signal
            self.gui_manager.draw_widgets()
            mouse_rect = Rect(self.mouse_position[0] - 3, self.mouse_position[1], 16, 16)
            mouse_bitmap = cut(self.screen, mouse_rect)
            self.screen.blit(self.cursor_image, mouse_rect)
            clock.tick(fps)
            pygame.display.flip()
            self.screen.blit(mouse_bitmap, mouse_rect)
            self.gui_manager.undraw_widgets()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                self.mouse_position = event.pos
            gui_event = self.gui_manager.handle_event(event)
            if gui_event != None:
                if gui_event == 'play':
                    return 'play'
                elif gui_event == 'exit':
                    return 'exit'
            else:
                if event.type == QUIT:
                    return 'exit'
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return 'exit'
        return None