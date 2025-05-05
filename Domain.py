import pygame
from pygame import FULLSCREEN, SCALED
from components import utility
from components.utility import file_resource, image_alpha
from components.gui.guimanager import colours
from components.scenes.mainmenu import MainMenu
from components.scenes.game import Game

class Main:
    def __init__(self):
        # initialize pygame
        pygame.init()
        # set the default font for utility functions
        utility.font_size = 16
        utility.font_object = pygame.font.Font(file_resource('fonts', 'Ubuntu', 'Ubuntu-Medium.ttf'), utility.font_size)
        # load tile sheet for utility functions
        utility.tiles = pygame.image.load(file_resource('domains', 'ProjectUtumno_full.png'))
        # create main window surface
        self.screen = pygame.display.set_mode((1920, 1080), FULLSCREEN | SCALED)
        # set the screen in utility
        utility.screen = self.screen
        utility.colours = colours
        # set window caption
        pygame.display.set_caption('Domain')
        # hide system mouse pointer
        pygame.mouse.set_visible(False)
        # set window icon
        pygame.display.set_icon(image_alpha('icon.png'))

    def run(self):
        while True:
            choice = MainMenu(self.screen).run()
            if choice == 0:
                break
            elif choice == 1:
                Game(self.screen).run()
        # release resources
        pygame.quit()

if __name__ == '__main__':
    Main().run()
