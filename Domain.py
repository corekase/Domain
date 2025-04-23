import time
import pygame
from pygame import Rect, FULLSCREEN, SCALED
from components.domain.domainmanager import DomainManager
from components.object.domainobject import DomainObject
from components.gui.guimanager import GuiManager, colours
from components import utility
from components.utility import file_resource, image_alpha, padding, render_text
from components.gui.frame import Frame
from components.gui.label import Label
from components.gui.pushbuttongroup import PushButtonGroup
from components.gui.scrollbar import Scrollbar
from components.gui.button import Button
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_F1
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, MOUSEWHEEL

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
        # set window caption
        pygame.display.set_caption('Domain')
        # hide system mouse pointer
        pygame.mouse.set_visible(False)
        # set window icon
        pygame.display.set_icon(image_alpha('icon.png'))
        # load images for custom mouse pointer
        self.cursor_image = image_alpha('cursors', 'normal.png')
        # dimensions of the map viewport
        view_xpos, view_ypos, view_width, view_height = 10, 10, 1600, 1040
        # create a surface of the view width and height size for rendering
        self.view_surface = pygame.Surface((view_width, view_height)).convert()
        # create a collision rect for the surface size for interface logic
        self.view_surface_rect = Rect(view_xpos, view_ypos, view_width, view_height)
        # create a rect that outlines view_surface_rect and the scrollbars
        self.view_surface_outline_rect = Rect(view_xpos - 1, view_ypos - 1, view_width + 20, view_height + 20)
        # create domain manager
        self.domain_manager = DomainManager(self.view_surface)
        # give domain objects a reference to the domain manager
        DomainObject.domain_manager = self.domain_manager
        # create a gui manager
        self.gui_manager = GuiManager(self.screen)
        # give domain objects a reference to the gui manager
        DomainObject.gui_manager = self.gui_manager
        # area for gui elements
        gui_xpos = view_xpos + view_width + 30
        gui_width = 1920 - gui_xpos - 10
        # create a rect for the information panel
        self.information_frame_rect = Rect(gui_xpos, 10, gui_width, padding(2) + 4)
        # create information panel frame
        self.gui_manager.add_widget('global', Frame('info_frame', self.information_frame_rect))
        # button width and height
        button_width, button_height = int(gui_width / 2), 22
        # set up the floor buttons
        floor_label = Label((gui_xpos, self.information_frame_rect.bottom + 5), 'Floor:')
        floor_0_rect = Rect(floor_label.rect.right + 4, self.information_frame_rect.bottom + 4, button_height, button_height)
        floor_1_rect = Rect(floor_0_rect.right + 4, self.information_frame_rect.bottom + 4, button_height, button_height)
        floor_0 = PushButtonGroup('floor0', floor_0_rect, '1', 'floors')
        floor_1 = PushButtonGroup('floor1', floor_1_rect, '2', 'floors')
        # pass the group push button widgets to the domain manager and push the button for which floor is active
        DomainManager.floor_group = (floor_0, floor_1)
        DomainManager.floor_group[self.domain_manager.floor].select()
        # scrollbars
        self.hbar = Scrollbar('hbar', (view_xpos + 1, view_ypos + view_height + 1, view_width, 17), True)
        self.vbar = Scrollbar('vbar', (view_xpos + view_width + 1, view_ypos + 1, 17, view_height), False)
        frame = Frame('none', (view_xpos + view_width + 1, view_ypos + view_height + 1, 17, 17))
        # global widgets
        self.gui_manager.add_widget('global', floor_label)
        self.gui_manager.add_widget('global', floor_0)
        self.gui_manager.add_widget('global', floor_1)
        self.gui_manager.add_widget('global', self.hbar)
        self.gui_manager.add_widget('global', self.vbar)
        self.gui_manager.add_widget('global', frame)
        # pickup and putdown rect
        area_1_rect = Rect(gui_xpos, floor_0_rect.bottom + 4, button_width, button_height)
        # won and exit rect
        area_2_rect = Rect(gui_xpos + button_width, self.screen.get_rect().bottom - button_height - 10 + 1,
                           button_width, button_height)
        # exit button
        exit_button = Button('exit', area_2_rect, 'Exit')
        # default context
        self.gui_manager.add_widget('default', exit_button)
        # pickup button context
        self.gui_manager.add_widget('pickup_context', Button('pick_up', area_1_rect, 'Pick Up'))
        self.gui_manager.add_widget('pickup_context', exit_button)
        # putdown button context
        self.gui_manager.add_widget('putdown_context', Button('put_down', area_1_rect, 'Put Down'))
        self.gui_manager.add_widget('putdown_context', exit_button)
        # game won context
        self.gui_manager.add_widget('win_context', Button('won', area_2_rect, 'Won!'))
        # switch to default context
        self.gui_manager.switch_context('default')
        # mouse position
        self.mouse_position = pygame.mouse.get_pos()
        # state for whether or not dragging the view
        self.dragging = False
        # toggle for following the avatar
        self.follow_avatar = False
        # whether to show absolute x and y, or x and y relative to floor
        self.coordinate_toggle = True
        # text status containing the x and y map indexes of the mouse position
        self.status = None
        # Set the state of the application to "running"
        self.running = True

    def run(self):
        # is the game won flag
        won = False
        # maximum frames-per-second, 0 for unlimited
        fps = 60
        # instantiate a pygame clock for frame maximum limits
        clock = pygame.time.Clock()
        # track elapsed_time with more accurate os clock
        previous_time = time.time()
        # clear main surface
        self.screen.fill(colours['background'])
        # continue while the running flag is true
        while self.running:
            # update scroll bar states
            self.update_scroll_bars()
            # handle events
            self.handle_events()
            # manage time
            now_time = time.time()
            elapsed_time = now_time - previous_time
            previous_time = now_time
            if not won:
                # update whether to follow the avatar through teleporters
                self.domain_manager.avatar.follow = self.follow_avatar
                # update domain state
                self.domain_manager.update_domain(elapsed_time)
                # if follow_avatar centre on avatar, after update_domain to avoid jitter
                if self.follow_avatar:
                    self.domain_manager.main_viewport = list(self.domain_manager.avatar.rect.center)
            # draw the outline around the main viewport
            pygame.draw.rect(self.screen, colours['light'], self.view_surface_outline_rect, 1)
            # draw the main viewport to the viewport surface
            self.domain_manager.draw_domain()
            # copy domain view surface into the main screen surface
            self.screen.blit(self.view_surface, self.view_surface_rect)
            # draw gui widgets
            self.gui_manager.draw_widgets()
            # update self.status for the information panel
            self.update_status()
            # draw information panel
            self.draw_info_panel(clock.get_fps())
            # position is relative to the hot-spot for the cursor image, which is (-6, 0) here.
            position = self.mouse_position[0] - 6, self.mouse_position[1]
            # mouse damage to background. tracking damage is much faster than filling entire screen
            damaged_rect = Rect(position[0], position[1], 16, 16)
            # blit the mouse cursor image to the screen
            self.screen.blit(self.cursor_image, position)
            # limit frames-per-second
            clock.tick(fps)
            # swap screen buffers
            pygame.display.flip()
            # fill mouse damaged area
            self.screen.fill(colours['background'], damaged_rect)
            # fill gui damaged areas
            for widget in (self.gui_manager.widgets[self.gui_manager.context] + self.gui_manager.widgets['global']):
                self.screen.fill(colours['background'], widget.rect)
            # check for winning conditions after gui damage has been filled as the gui context may be changed
            if not won:
                if self.domain_manager.check_win():
                    # display winning screen here
                    self.gui_manager.lock_context('win_context')
                    won = True
        # release resources
        pygame.quit()

    def update_scroll_bars(self):
        # get the view and map rects for the scrollbars
        view_rect = self.domain_manager.renderer.view_rect
        map_rect = self.domain_manager.renderer.map_rect
        # update the horizontal scrollbar data, subtract the floor from the view rect then the hbar is normalized
        self.hbar.set(map_rect.width / self.domain_manager.floors,
                      view_rect.x - (self.domain_manager.floor * self.domain_manager.floor_size), view_rect.width)
        # update the vertical scrollbar data
        self.vbar.set(map_rect.height, view_rect.y, view_rect.height)

    def handle_events(self):
        # handle event queue
        for event in pygame.event.get():
            gui_event = self.gui_manager.handle_event(event)
            if gui_event != None:
                # handle gui events
                if gui_event in ('floor0', 'floor1'):
                    # switch floors
                    if gui_event == 'floor0':
                        self.domain_manager.switch_floor(0)
                    else:
                        self.domain_manager.switch_floor(1)
                    # stop following avatar
                    self.follow_avatar = False
                elif gui_event in ('hbar', 'vbar'):
                    # scrollbar adjusted
                    if gui_event == 'hbar':
                        # hbar changed, add floor back into the view port and update viewport
                        self.domain_manager.renderer.view_rect.left = self.hbar.get() + (self.domain_manager.floor * self.domain_manager.floor_size)
                    else:
                        # the vbar was changed, update viewport
                        self.domain_manager.renderer.view_rect.top = self.vbar.get()
                    # update the main viewport after scrollbar adjustment
                    self.domain_manager.main_viewport = list(self.domain_manager.renderer.view_rect.center)
                    # stop following avatar
                    self.follow_avatar = False
                elif gui_event == 'pick_up':
                    self.domain_manager.avatar.pick_up()
                elif gui_event == 'put_down':
                    self.domain_manager.avatar.put_down()
                elif (gui_event == 'won') or (gui_event == 'exit'):
                    self.running = False
                # update the mouse position if it was a motion event
                if event.type == MOUSEMOTION:
                    self.mouse_position = event.pos
            else:
                # handle other events
                if event.type == QUIT:
                    # window close widget
                    self.running = False
                # keys
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        # escape key, also quits
                        self.running = False
                    elif event.key == K_F1:
                        # toggle whether coordinates shown are relative or absolute
                        self.coordinate_toggle = not self.coordinate_toggle
                # mouse movement and dragging
                elif event.type == MOUSEMOTION:
                    if self.dragging:
                        # move the centre of the viewport
                        x, y = event.rel
                        self.domain_manager.main_viewport[0] += x
                        self.domain_manager.main_viewport[1] += y
                        # keep the physical mouse position within the view surface rect as much as possible
                        if not self.view_surface_rect.collidepoint(event.pos):
                            # outside of view surface rect, move physical mouse position to center of view_surface_rect
                            pygame.mouse.set_pos(self.view_surface_rect.center)
                    else:
                        # update the stored mouse position
                        self.mouse_position = event.pos
                # mouse buttons
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    # is mouse inside the view surface rect
                    if self.view_surface_rect.collidepoint(x, y):
                        if event.button == 1:
                            # left button, normalize mouse position to view surface rect screen position
                            view_x, view_y = x - self.view_surface_rect.x, y - self.view_surface_rect.y
                            # get cell position from normalized position
                            position = self.domain_manager.pixel_to_cell(view_x, view_y)
                            # attempt to move avatar to that position
                            self.domain_manager.avatar.move_to(position)
                        elif event.button == 2:
                            # mouse-wheel button, switch to the avatar floor and centre the main viewport on it
                            self.domain_manager.switch_floor(self.domain_manager.get_floor(self.domain_manager.avatar.coord))
                            self.domain_manager.main_viewport = list(self.domain_manager.avatar.rect.center)
                            # toggle follow_avatar between true and false
                            self.follow_avatar = not self.follow_avatar
                        elif event.button == 3:
                            # right button down, begin dragging state
                            self.dragging = True
                            # cancel follow
                            self.follow_avatar = False
                elif event.type == MOUSEBUTTONUP:
                    if (event.button == 3) and self.dragging:
                        # put the physical cursor back to the mouse position
                        pygame.mouse.set_pos(self.mouse_position)
                        # end dragging state
                        self.dragging = False
                elif event.type == MOUSEWHEEL:
                    # only zoom when the mouse position is within the view surface rect
                    if self.view_surface_rect.collidepoint(self.mouse_position):
                        # adjust the zoom level, event.y will either be a -1 or a 1
                        self.domain_manager.set_zoom_delta(event.y)

    def update_status(self):
        # update the x and y map indexes for the information panel
        x, y = self.mouse_position
        if self.view_surface_rect.collidepoint(x, y):
            # inside the view_surface_rect, get the cell coordinate
            x_coord, y_coord = self.domain_manager.pixel_to_cell(x - self.view_surface_rect.x, y - self.view_surface_rect.y)
            # show relative-to-floor or absolute coordinates
            if self.coordinate_toggle:
                # these coordinates are relative-to-floor
                x_coord %= self.domain_manager.floor_tiles
                y_coord %= self.domain_manager.floor_tiles
            # update the status for the information panel
            self.status = f'X:{x_coord}, Y:{y_coord}'
        else:
            # not inside the surface rect
            self.status = 'N/A'

    def draw_info_panel(self, fps):
        fps = f'FPS: {int(round(fps))}'
        # layout coordinates
        x_pos, y_pos, _, _ = self.information_frame_rect
        # draw each text line onto the screen
        self.screen.blit(render_text(fps), (x_pos + 3, y_pos + padding(0)))
        self.screen.blit(render_text(self.status), (x_pos + 3, y_pos + padding(1)))

if __name__ == '__main__':
    Main().run()
