import time, pygame
from pygame import Rect
from pygame.draw import rect
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_1, K_2, K_3, K_F1
from components.utility import image_alpha_resource, padding, render_text
from components.gui.button import Button
from components.gui.frame import Frame
from components.gui.widget import colours
from components.gui.guimanager import GuiManager
from components.domain.domainmanager import DomainManager
from components.object.domainobject import DomainObject
from components import utility

class Main:
    def __init__(self):
        # initialize pygame
        pygame.init()
        # create main window surface
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
        # set window caption
        pygame.display.set_caption('Domain')
        # set window icon
        pygame.display.set_icon(image_alpha_resource('icon.png'))
        # hide system mouse pointer
        pygame.mouse.set_visible(False)
        # set the default font for utility functions
        utility.font_size = 16
        utility.font_object = pygame.font.Font(pygame.font.get_default_font(), utility.font_size)
        # load images for custom mouse pointers
        self.cursor_domain_image = image_alpha_resource('cursors', 'cursor_domain.png')
        self.cursor_interface_image = image_alpha_resource('cursors', 'cursor_interface.png')
        # state for whether or not panning the view
        self.panning = False
        # when panning lock mouse position to this position
        self.pan_hold_position = None
        # cycle counter
        self.cycle = -1
        # text status containing the x and y map indexes of the mouse position, updated in the event handler
        self.status = None
        # index into tiles is: 0 empty, 1 floor, and 2 wall. the value of the index is the tile gid
        # in other class components, define these at the top and use them as named indexes:
        # EMPTY, FLOOR, WALL = 0, 1, 2
        tiles = (3, 2, 1)
        # give both the domain manager and domain objects the tiles gid tuple
        DomainManager.tiles = tiles
        DomainObject.tiles = tiles
        # x and y position of the viewport
        view_xpos = 10
        view_ypos = 10
        # viewport size. renderer view_rect size at a given zoom must not be larger than renderer map_rect size
        # at the same zoom. if greater, pick_cell() in domain manager gives invalid results
        view_width = 1680
        view_height = 1060
        # create a surface of that size for rendering
        self.view_surface = pygame.Surface((view_width, view_height)).convert()
        # create a collision rect for the surface size for interface logic
        self.view_surface_rect = Rect(view_xpos, view_ypos, view_width, view_height)
        # create a rect that outlines view_surface_rect
        self.view_surface_outline_rect = Rect(view_xpos - 1, view_ypos - 1, view_width + 2, view_height + 2)
        # create domain manager
        self.domain_manager = DomainManager(self.view_surface)
        # give domain objects a reference to the domain manager
        DomainObject.domain_manager = self.domain_manager
        # instantiate a GUI manager
        self.gui = GuiManager()
        # give domain objects a reference to the gui
        DomainObject.gui = self.gui
        # base x position
        base_x = view_xpos + view_width + 10
        width_x = 1920 - base_x
        # create a frame for the information panel
        information_frame_rect = Rect(base_x, 0, 1920 - base_x, padding(4))
        self.information_frame = Frame(self.screen, 'info_frame', information_frame_rect)
        # create buttons and add them to gui context widgets lists
        w, h = int(width_x / 2), 20
        button_rect = Rect(base_x, padding(4) + 2, w, h)
        button_exit_rect = Rect(1920 - w - 4, 1080 - h - 4, w, h)
        exit_button = Button(self.screen, 'exit', button_exit_rect, 'Exit')
        # pickup button context
        self.gui.add_widget('pickup_context', Button(self.screen, 'pick_up', button_rect, 'Pick Up'))
        self.gui.add_widget('pickup_context', exit_button)
        # putdown button context
        self.gui.add_widget('putdown_context', Button(self.screen, 'put_down', button_rect, 'Put Down'))
        self.gui.add_widget('putdown_context', exit_button)
        # game won context
        self.gui.add_widget('win_context', Button(self.screen, 'won', button_rect, 'Won!'))
        # default context
        self.gui.add_widget('default', exit_button)
        # switch to default context
        self.gui.switch_context('default')
        # set won game condition to false
        self.won = False
        # Set the state of the application to "running"
        self.running = True
        # whether to show absolute x and y, or x and y relative to floor
        self.coordinate_toggle = True

    def run(self):
        # maximum frames-per-second, 0 for unlimited
        fps = 0
        # instantiate a pygame clock for frame maximum limits
        clock = pygame.time.Clock()
        # track elapsed_time with more accurate os clock
        previous_time = time.time()
        # continue while the running flag is true
        # fill clear_area_rect with a colour, this area isn't drawn over by anything else
        self.screen.fill(colours['background'])
        while self.running:
            # main loop
            self.cycle += 1
            # manage time
            now_time = time.time()
            elapsed_time = now_time - previous_time
            previous_time = now_time
            # handle events
            self.handle_events()
            # update domain state
            if not self.won:
                self.domain_manager.update_domain(elapsed_time)
            # draw the outline around the main viewport
            rect(self.screen, colours['light'], self.view_surface_outline_rect, 1)
            # draw the main viewport to the viewport surface
            self.domain_manager.draw_domain()
            # and copy that surface into the main screen surface
            self.screen.blit(self.view_surface, self.view_surface_rect)
            # draw gui widgets
            self.gui.draw_widgets()
            # draw information panel
            self.draw_info_panel(clock.get_fps())
            # draw mouse cursor
            x, y = pygame.mouse.get_pos()
            # mouse damage to background. tracking damage is much faster than filling entire screen
            damaged_rect = Rect(x - 16, y - 16, 32, 32)
            self.draw_mouse(x, y)
            # check for winning conditions
            if not self.won:
                if self.check_win():
                    # display winning screen here
                    self.gui.lock_context('win_context')
                    self.won = True
            # limit frames-per-second
            clock.tick(fps)
            # swap screen buffers
            pygame.display.flip()
            # fill mouse damage
            self.screen.fill(colours['background'], damaged_rect)
            # fill gui damage
            for widget in self.gui.widgets[self.gui.context]:
                self.screen.fill(colours['background'], Rect(widget.rect.x - 1, widget.rect.y - 1,
                                                             widget.rect.width + 2, widget.rect.height + 2))
        # release resources
        pygame.quit()

    def handle_events(self):
        # handle event queue
        for event in pygame.event.get():
            gui_event = self.gui.handle_event(event)
            if gui_event != None:
                # handle gui events
                if gui_event == 'pick_up':
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
                    if event.key == K_1:
                        self.domain_manager.switch_floor(0)
                    elif event.key == K_2:
                        self.domain_manager.switch_floor(1)
                    elif event.key == K_3:
                        self.domain_manager.switch_floor(2)
                    elif event.key == K_F1:
                        self.coordinate_toggle = not self.coordinate_toggle
                # mouse buttons
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    # if mouse is inside the view rect
                    if self.view_surface_rect.collidepoint(x, y):
                        if event.button == 3:
                            # right button down, begin panning state
                            self.panning = True
                            self.pan_hold_position = x, y
                        elif event.button == 4:
                            # wheel scroll up, increase zoom index
                            self.domain_manager.set_zoom_index(1)
                            # if right-mouse button is also pressed begin panning
                            if pygame.mouse.get_pressed()[2]:
                                self.panning = True
                                self.pan_hold_position = x, y
                        elif event.button == 5:
                            # wheel scroll down, decrease zoom index
                            self.domain_manager.set_zoom_index(-1)
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        # left button up, which is destination point for avatar
                        x, y = event.pos
                        # if mouse is inside the view rect
                        if self.view_surface_rect.collidepoint(x, y):
                            position = self.domain_manager.pick_cell(x -self.view_surface_rect.x, y - self.view_surface_rect.y)
                            self.domain_manager.avatar.move_to(position)
                    if event.button == 3:
                        # right button up, end panning state
                        self.panning = False
                # panning state actions
                if self.panning:
                    # if the mouse is moving
                    if event.type == MOUSEMOTION:
                        # move the centre of the viewport
                        x, y = event.pos
                        self.domain_manager.main_viewport[0] += x - self.pan_hold_position[0]
                        self.domain_manager.main_viewport[1] += y - self.pan_hold_position[1]
                        pygame.mouse.set_pos(self.pan_hold_position)
        # update the x and y map indexes for the information panel
        x, y = pygame.mouse.get_pos()
        if self.view_surface_rect.collidepoint(x, y):
            x_coord, y_coord = self.domain_manager.pick_cell(x - self.view_surface_rect.x, y - self.view_surface_rect.y)
            if self.coordinate_toggle:
                x_coord %= self.domain_manager.floor_tiles
                y_coord %= self.domain_manager.floor_tiles
            # update the status for the information panel
            self.status = f'X:{x_coord}, Y:{y_coord}'
        else:
            # not inside the surface rect
            self.status = "N/A"

    def check_win(self):
        # if all the pickup items are in the same cell then the game is won
        matched = True
        last_item = None
        objects = self.domain_manager.domain.objects('pickups')
        # if the avatar has an item in their inventory then include it
        if self.domain_manager.avatar.inventory != None:
            objects.append(self.domain_manager.avatar.inventory)
        # compare cell coordinates for all items, if any don't match then the check fails
        # the last item in the avatar inventory doesn't count until it's placed on the map
        # because its coordinates aren't updated until then
        for item in objects:
            if last_item == None:
                last_item = item
                continue
            if (item.x_coord != last_item.x_coord) or (item.y_coord != last_item.y_coord):
                matched = False
                break
        # if true then won
        return matched

    def draw_info_panel(self, fps):
        # gather information into text strings
        cycle = f'Cycle: {self.cycle}'
        fps = f'FPS: {int(round(fps))}'
        floor = f'Floor: {self.domain_manager.floor + 1}'
        # draw frame
        self.information_frame.draw()
        # layout coordinates
        x_pos, y_pos, _, _ = self.information_frame.rect
        # draw each text line onto the screen
        self.screen.blit(render_text(cycle), (x_pos + 3, y_pos + padding(0)))
        self.screen.blit(render_text(fps), (x_pos + 3, y_pos + padding(1)))
        self.screen.blit(render_text(floor), (x_pos + 3, y_pos + padding(2)))
        # status is constantly updated in the event handler
        self.screen.blit(render_text(self.status), (x_pos + 3, y_pos + padding(3)))

    def draw_mouse(self, x, y):
        # draw mouse cursor
        # is the mouse in the view rect?
        if self.view_surface_rect.collidepoint(x, y):
            # draw domain cursor
            self.screen.set_clip(self.view_surface_rect)
            if self.panning:
                self.screen.blit(self.cursor_domain_image,
                                (self.pan_hold_position[0] - 15, self.pan_hold_position[1] - 15))
            else:
                self.screen.blit(self.cursor_domain_image, (x - 15, y - 15))
            self.screen.set_clip(None)
        else:
            # outside of view surface rect, draw interface cursor
            self.screen.blit(self.cursor_interface_image, (x - 6, y))

if __name__ == '__main__':
    Main().run()
