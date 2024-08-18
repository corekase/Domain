import time
import pygame
from pygame import Rect
from components.domain.domainmanager import DomainManager
from components.object.domainobject import DomainObject
from components.gui.guimanager import GuiManager, colours
from components import utility
from components.utility import file_resource, padding, render_text
from components.gui.label import Label
from components.gui.pushbuttongroup import PushButtonGroup
from components.gui.frame import Frame
from components.gui.button import Button
from components.gui.scrollbar import Scrollbar
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_F1
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

class Main:
    def __init__(self):
        # tile_gid is a ordered tuple containing Tiled map gid numbers. if gid's change only here needs to be updated
        # indexes are named: EMPTY, WALL, FLOOR = 0, 1, 2 (for the values of 0, 1, 2 in tile_gid)
        tile_gid = (0, 1, 2)
        # give both the domain manager and domain objects the tile_gid tuple
        DomainManager.tile_gid = tile_gid
        DomainObject.tile_gid = tile_gid
        # initialize pygame
        pygame.init()
        # set the default font for utility functions
        utility.font_size = 18
        utility.font_object = pygame.font.Font(file_resource('fonts', 'Ubuntu', 'Ubuntu-Medium.ttf'), utility.font_size)
        # create main window surface
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
        # set window caption
        pygame.display.set_caption('Domain')
        # hide system mouse pointer
        pygame.mouse.set_visible(False)
        # set window icon
        pygame.display.set_icon(utility.image_alpha('icon.png'))
        # load images for custom mouse pointer
        self.cursor_image = utility.image_alpha('cursors', 'normal.png')
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
        self.gui_manager = GuiManager()
        # give domain objects a reference to the gui manager
        DomainObject.gui_manager = self.gui_manager
        # area for gui elements
        gui_xpos = view_xpos + view_width + 30
        gui_width = 1920 - gui_xpos - 10
        # create a rect for the information panel
        information_frame_rect = Rect(gui_xpos, 10, gui_width, padding(2) + 4)
        # create information panel frame
        self.information_frame = Frame(self.screen, 'info_frame', information_frame_rect)
        # button width and height
        button_width, button_height = int(gui_width / 2), 22
        # set up the floor buttons
        floor_label = Label(self.screen, (gui_xpos, information_frame_rect.bottom + 4), 'Floor:')
        floor_1_rect = Rect(floor_label.rect.right + 4, information_frame_rect.bottom + 4, button_height, button_height)
        floor_2_rect = Rect(floor_1_rect.right + 4, information_frame_rect.bottom + 4, button_height, button_height)
        floor0 = PushButtonGroup(self.screen, 'floor0', floor_1_rect, '1', 'floors')
        floor1 = PushButtonGroup(self.screen, 'floor1', floor_2_rect, '2', 'floors')
        self.floors = [floor0, floor1]
        self.floors[self.domain_manager.floor].select()
        # scrollbars
        self.hbar = Scrollbar(self.screen, 'hbar', (view_xpos + 1, view_ypos + view_height + 1, view_width, 17), True)
        self.vbar = Scrollbar(self.screen, 'vbar', (view_xpos + view_width + 1, view_ypos + 1, 17, view_height), False)
        frame = Frame(self.screen, 'none', (view_xpos + view_width + 1, view_ypos + view_height + 1, 17, 17))
        # pickup and putdown rect
        area_1_rect = Rect(gui_xpos, floor_1_rect.bottom + 4, button_width, button_height)
        # won and exit rect, '22' accounts for the scroll bar
        area_2_rect = Rect(gui_xpos + button_width, self.view_surface_rect.bottom - button_height + 22,
                          button_width, button_height)
        # pickup button context
        self.gui_manager.add_widget('pickup_context', Button(self.screen, 'pick_up', area_1_rect, 'Pick Up'))
        # putdown button context
        self.gui_manager.add_widget('putdown_context', Button(self.screen, 'put_down', area_1_rect, 'Put Down'))
        # game won context
        self.gui_manager.add_widget('win_context', Button(self.screen, 'won', area_2_rect, 'Won!'))
        # exit button
        exit_button = Button(self.screen, 'exit', area_2_rect, 'Exit')
        # add common controls to all contexts, also creates default context
        for context in ('pickup_context', 'putdown_context', 'win_context', 'default'):
            self.gui_manager.add_widget(context, floor_label)
            self.gui_manager.add_widget(context, self.floors[0])
            self.gui_manager.add_widget(context, self.floors[1])
            self.gui_manager.add_widget(context, self.hbar)
            self.gui_manager.add_widget(context, self.vbar)
            self.gui_manager.add_widget(context, frame)
            if context != 'win_context':
                self.gui_manager.add_widget(context, exit_button)
        # switch to default context
        self.gui_manager.switch_context('default')
        # state for whether or not panning the view
        self.panning_state = False
        # when panning lock mouse position to this position
        self.panning_state_position = None
        # toggle state for following the avatar
        self.follow_state = False
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
        fps = 0
        # maximum frame time, if above this switch to non-realtime movement
        max_time = 1000 / 60
        # instantiate a pygame clock for frame maximum limits
        clock = pygame.time.Clock()
        # track elapsed_time with more accurate os clock
        previous_time = time.time()
        # clear main surface
        self.screen.fill(colours['background'])
        # continue while the running flag is true
        while self.running:
            # update scroll bar states
            self.update_scroll_bar_states()
            # handle events
            self.handle_events()
            # manage time
            now_time = time.time()
            elapsed_time = now_time - previous_time
            previous_time = now_time
            # if a frame takes longer than max time then switch to non-realtime movement
            if elapsed_time > max_time:
                elapsed_time = max_time
            # update domain state
            if not won:
                self.domain_manager.update_domain(elapsed_time)
            # if follow_state centre on avatar, after update_domain to fix jitter
            if self.follow_state:
                self.domain_manager.main_viewport = list(self.domain_manager.avatar.rect.center)
            # draw the outline around the main viewport
            pygame.draw.rect(self.screen, colours['light'], self.view_surface_outline_rect, 1)
            # draw the main viewport to the viewport surface
            self.domain_manager.draw_domain()
            # copy domain view surface into the main screen surface
            self.screen.blit(self.view_surface, self.view_surface_rect)
            # draw gui widgets
            self.gui_manager.draw_widgets()
            # poll for mouse position
            x, y = pygame.mouse.get_pos()
            # mouse damage to background. tracking damage is much faster than filling entire screen
            damaged_rect = Rect(x - 6, y, 16, 16)
            # update self.status for the information panel
            self.update_status(x, y)
            # draw information panel
            self.draw_info_panel(clock.get_fps())
            # draw mouse cursor
            self.draw_mouse(x, y)
            # limit frames-per-second
            clock.tick(fps)
            # swap screen buffers
            pygame.display.flip()
            # fill mouse damaged area
            self.screen.fill(colours['background'], damaged_rect)
            # fill gui damaged areas
            for widget in self.gui_manager.widgets[self.gui_manager.context]:
                self.screen.fill(colours['background'], widget.rect)
            # check for winning conditions after gui damage has been filled as the gui context may be changed
            if not won:
                if self.domain_manager.check_win():
                    # display winning screen here
                    self.gui_manager.lock_context('win_context')
                    won = True
        # release resources
        pygame.quit()

    def update_scroll_bar_states(self):
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
                    # stop following on any floor switch
                    self.follow_state = False
                    # switch floors
                    if gui_event == 'floor0':
                        self.domain_manager.switch_floor(0)
                    else:
                        self.domain_manager.switch_floor(1)
                    # update which button is selected
                    self.floors[self.domain_manager.floor].select()
                elif gui_event in ('hbar', 'vbar'):
                    # stop following if a scrollbar is adjusted
                    self.follow_state = False
                    if gui_event == 'hbar':
                        # hbar changed, add floor back into the view port and update
                        self.domain_manager.renderer.view_rect.left = self.hbar.get() + (self.domain_manager.floor * self.domain_manager.floor_size)
                    else:
                        # the vbar was changed, update viewport
                        self.domain_manager.renderer.view_rect.top = self.vbar.get()
                    # update the main viewport after scrollbar adjustment
                    self.domain_manager.main_viewport = list(self.domain_manager.renderer.view_rect.center)
                elif gui_event == 'pick_up':
                    self.domain_manager.avatar.pick_up()
                elif gui_event == 'put_down':
                    self.domain_manager.avatar.put_down()
                elif (gui_event == 'won') or (gui_event == 'exit'):
                    self.running = False
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
                # mouse buttons
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    # if mouse is inside the view rect
                    if self.view_surface_rect.collidepoint(x, y):
                        if event.button == 1:
                            # left button click, which is destination point for avatar
                            x, y = event.pos
                            # if mouse is inside the view rect
                            if self.view_surface_rect.collidepoint(x, y):
                                position = self.domain_manager.pick_cell(x - self.view_surface_rect.x, y - self.view_surface_rect.y)
                                self.domain_manager.avatar.move_to(position)
                        elif event.button == 2:
                            # switch to the avatar floor and centre the main viewport on it
                            self.domain_manager.switch_floor(self.domain_manager.get_floor(self.domain_manager.avatar.coord))
                            self.domain_manager.main_viewport = list(self.domain_manager.avatar.rect.center)
                            # toggle between follow_state true and false
                            self.follow_state = not self.follow_state
                        elif event.button == 3:
                            # cancel follow_state
                            self.follow_state = False
                            # right button down, begin panning state
                            self.panning_state = True
                            self.panning_state_position = x, y
                        elif event.button == 4:
                            # wheel scroll up, increase zoom index
                            self.domain_manager.set_zoom_index(1)
                            # if right-mouse button is also pressed begin panning
                            if pygame.mouse.get_pressed()[2]:
                                self.panning_state = True
                                self.panning_state_position = x, y
                        elif event.button == 5:
                            # wheel scroll down, decrease zoom index
                            self.domain_manager.set_zoom_index(-1)
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 3:
                        # right button up, end panning state
                        self.panning_state = False
                # panning state actions
                if self.panning_state:
                    # if the mouse is moving
                    if event.type == MOUSEMOTION:
                        # move the centre of the viewport
                        x, y = event.pos
                        self.domain_manager.main_viewport[0] += x - self.panning_state_position[0]
                        self.domain_manager.main_viewport[1] += y - self.panning_state_position[1]
                        pygame.mouse.set_pos(self.panning_state_position)

    def update_status(self, x, y):
        # update the x and y map indexes for the information panel
        if self.view_surface_rect.collidepoint(x, y):
            # inside the view_surface_rect, pick the cell coordinates
            x_coord, y_coord = self.domain_manager.pick_cell(x - self.view_surface_rect.x, y - self.view_surface_rect.y)
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
        # draw frame
        self.information_frame.draw()
        # layout coordinates
        x_pos, y_pos, _, _ = self.information_frame.rect
        # draw each text line onto the screen
        self.screen.blit(render_text(fps), (x_pos + 3, y_pos + padding(0)))
        self.screen.blit(render_text(self.status), (x_pos + 3, y_pos + padding(1)))

    def draw_mouse(self, x, y):
        # draw mouse cursor
        if self.panning_state:
            self.screen.blit(self.cursor_image,
                            (self.panning_state_position[0] - 6, self.panning_state_position[1]))
        else:
            self.screen.blit(self.cursor_image, (x - 6, y))

if __name__ == '__main__':
    Main().run()
