import pygame
from pygame import Rect, QUIT
from pygame.locals import MOUSEMOTION, KEYDOWN, K_ESCAPE
from components.gui.guimanager import GuiManager, colours
from components.gui.frame import Frame
from components.gui.button import Button
from components.gui.label import Label
from components.utility import image_alpha, cut, file_resource

class MainMenu:
    def __init__(self, screen):
        # main window surface
        self.screen = screen
        self.width = 200
        self.height = 80
        self.x = int((self.screen.get_rect().width - self.width) / 2)
        self.y = int((self.screen.get_rect().height - self.height) / 2)
        self.frame_rect = Rect(self.x, self.y, self.width, self.height)
        self.gui_manager = GuiManager(self.screen)
        self.gui_manager.add_widget('menu', Frame('frame', self.frame_rect))
        label = Label((0, 0), 'Main Menu')
        label.rect.x = int((self.screen.get_rect().width - label.rect.width) / 2)
        label.rect.y = self.y + 2
        self.gui_manager.add_widget('menu', label)
        self.gui_manager.add_widget('menu', Button('play',
                        Rect(self.x + 10, self.y + 25, self.width - 20, 20), 'Play'))
        self.gui_manager.add_widget('menu', Button('exit',
                        Rect(self.x + 10, self.y + 50, self.width - 20, 20), 'Exit'))
        self.gui_manager.switch_context('menu')
        self.cursor_image = image_alpha('cursors', 'normal.png')
        self.mouse_position = pygame.mouse.get_pos()
        # set a background image
        self.screen.blit(pygame.image.load(file_resource('images', 'backdrop.jpg')).convert(), (0, 0))

    def run(self):
        fps = 60
        clock = pygame.time.Clock()
        while True:
            signal = self.handle_events()
            if signal != None:
                return signal
            self.gui_manager.draw_widgets()
            position = Rect(self.mouse_position[0] - 6, self.mouse_position[1], 16, 16)
            bitmap = cut(self.screen, position)
            self.screen.blit(self.cursor_image, position)
            clock.tick(fps)
            pygame.display.flip()
            self.screen.blit(bitmap, position)
            # fill gui damaged areas
            self.gui_manager.undraw_widgets()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                self.mouse_position = event.pos
            gui_event = self.gui_manager.handle_event(event)
            if gui_event != None:
                if gui_event == 'play':
                    return 1
                elif gui_event == 'exit':
                    return 0
            else:
                if event.type == QUIT:
                    return 0
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return 0
        return None