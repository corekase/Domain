import os
if os.name == 'nt':
    # corrects graphical scaling issues with Windows
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
import pygame
from pygame import FULLSCREEN, SCALED
# importing utility initializes its namespace for its functions
from components import utility
from components.utility import file_resource, image_alpha
from components.scenes.mainmenu import MainMenu
from components.scenes.game import Game

class Main:
    def __init__(self):
        # initialize pygame
        pygame.init()
        # create main window surface
        self.screen = pygame.display.set_mode((1920, 1080), FULLSCREEN | SCALED, vsync=1)
        # set window caption
        pygame.display.set_caption('Domain')
        # hide system mouse pointer
        pygame.mouse.set_visible(False)
        # set window icon
        pygame.display.set_icon(image_alpha('icon.png'))
        # set the screen in utility
        utility.screen = self.screen
        # set the default font for utility functions
        utility.font_size = 16
        utility.font_object = pygame.font.Font(file_resource('fonts', 'Ubuntu', 'Ubuntu-Medium.ttf'), utility.font_size)
        # load tile sheet for utility functions
        utility.tiles = pygame.image.load(file_resource('domains', 'ProjectUtumno_full.png'))

    def run(self):
        while True:
            choice = MainMenu(self.screen).run()
            if choice == 'exit':
                break
            elif choice == 'play':
                Game(self.screen).run()
        # release resources
        pygame.quit()

if __name__ == '__main__':
    Main().run()
