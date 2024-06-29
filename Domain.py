import time, pygame
from pygame import Rect
from components.utility import image_alpha_resource, padding, render
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from components.gui.button import Button
from components.gui.frame import Frame
from components.gui.widget import colours
from components import utility
from components.gui.guimanager import GuiManager
from components.map.mapmanager import MapManager
from components.object.domainobject import DomainObject

class Main:
    def __init__(self):
        # fullscreen?
        fullscreen = True
        # initialize pygame
        pygame.init()
        # create main window surface
        if fullscreen:
            self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
        else:
            self.screen = pygame.display.set_mode((1700, 1000))
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
        self.cursor_normal_image = image_alpha_resource('cursors', 'cursor_normal_x7_y7.png')
        self.cursor_panning_image = image_alpha_resource('cursors', 'cursor_pan_x7_y7.png')
        self.cursor_interface_image = image_alpha_resource('cursors', 'cursor_interface_x6_y0.png')
        # state for whether or not panning the view
        self.panning = False
        # when panning lock mouse position to this position
        self.pan_hold_position = None
        # cycle counter, to be used for demo recording, marking, and playback later
        self.cycle = -1
        # text status containing the x and y map indexes of the mouse position, updated in the event handler
        self.status = None
        # calculate view size at 1.0 zoom
        view_width = 600
        view_height = 600
        # create a surface of that size for rendering
        self.view_surface = pygame.Surface((view_width, view_height)).convert()
        # for that surface, centre both the x and y axis relative to the screen surface
        view_xpos = (self.screen.get_rect().width - view_width) // 2
        view_ypos = (self.screen.get_rect().height - view_height) // 2
        # create a collision rect for the surface size for interface logic
        self.view_surface_rect = Rect(view_xpos, view_ypos, 960, 960)
        # create a rect for a border colour around the view surface
        self.view_surface_border_rect = Rect(view_xpos - 1, view_ypos - 1, view_width + 2, view_height + 2)
        # create renderer
        self.map_manager = MapManager(self.view_surface)
        # instantiate a GUI manager
        self.gui = GuiManager()
        # give the map object access to gui switch context
        MapManager.gui = self.gui
        DomainObject.gui = self.gui
        # create a frame
        information_frame_rect = (self.screen.get_rect().right - 170, 10, 160, padding(4))
        self.information_frame = Frame(self.screen, 'info_frame', information_frame_rect)
        # create buttons and add them to gui context widgets lists
        w, h = 120, 20
        button_rect = (self.screen.get_rect().right - w - 10, self.screen.get_rect().bottom - h - 10, w, h)
        # pickup button context
        self.gui.add_widget('pickup_context', Button(self.screen, 'pick_up', button_rect, 'Pick Up'))
        # putdown button context
        self.gui.add_widget('putdown_context', Button(self.screen, 'put_down', button_rect, 'Put Down'))
        # game won context
        self.gui.add_widget('win_context', Button(self.screen, 'won', button_rect, 'Won!'))
        # set won game condition to false
        self.won = False
        # Set the state of the application to "running"
        self.running = True

    def run(self):
        # maximum frames-per-second, 0 for unlimited
        fps = 0
        # instantiate a pygame clock for frame maximum limits
        clock = pygame.time.Clock()
        # track elapsed_time with more accurate os clock
        previous_time = time.time()
        # total time for information panel
        total_time = 0.0
        # continue while the running flag is true
        while self.running:
            # main loop
            self.cycle += 1
            # manage time
            now_time = time.time()
            elapsed_time = now_time - previous_time
            previous_time = now_time
            total_time += elapsed_time
            # handle events
            self.handle_events()
            # update domain state
            if not self.won:
                self.map_manager.update_domain(elapsed_time)
            # clear screen
            self.screen.fill(colours['background'])
            # draw the main viewport to the viewport surface
            self.map_manager.draw_domain()
            # and copy that surface into the main screen surface
            self.screen.blit(self.view_surface, self.view_surface_rect)
            # draw a rectangle colour around it
            pygame.draw.rect(self.screen, (255, 255, 255), self.view_surface_border_rect, 1)
            # draw gui widgets
            self.gui.draw_widgets()
            # draw information panel
            self.draw_info_panel(total_time, clock.get_fps())
            # draw mouse cursor
            self.draw_mouse()
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
        # release resources
        pygame.quit()

    def handle_events(self):
        # handle event queue
        for event in pygame.event.get():
            gui_event = self.gui.handle_event(event)
            if gui_event != None:
                # handle gui events
                if gui_event == 'pick_up':
                    self.map_manager.avatar.pick_up()
                elif gui_event == 'put_down':
                    self.map_manager.avatar.put_down()
                elif gui_event == 'won':
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
                            self.map_manager.set_zoom_index(1)
                            # if right-mouse button is also pressed begin panning
                            if pygame.mouse.get_pressed()[2]:
                                self.panning = True
                                self.pan_hold_position = x, y
                        elif event.button == 5:
                            # wheel scroll down, decrease zoom index
                            self.map_manager.set_zoom_index(-1)
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        # left button up, which is destination point for avatar
                        x, y = event.pos
                        # if mouse is inside the view rect
                        if self.view_surface_rect.collidepoint(x, y):
                            position = self.map_manager.pick_cell(x -self.view_surface_rect.x, y - self.view_surface_rect.y)
                            self.map_manager.avatar.move_to(position)
                    if event.button == 3:
                        # right button up, end panning state
                        self.panning = False
                # panning state actions
                if self.panning:
                    # if the mouse is moving
                    if event.type == MOUSEMOTION:
                        # move the centre of the viewport
                        x, y = event.pos
                        self.map_manager.main_viewport[0] += x - self.pan_hold_position[0]
                        self.map_manager.main_viewport[1] += y - self.pan_hold_position[1]
                        pygame.mouse.set_pos(self.pan_hold_position)
        # update the x and y map indexes for the information panel
        x, y = pygame.mouse.get_pos()
        if self.view_surface_rect.collidepoint(x, y):
            x_coord, y_coord = self.map_manager.pick_cell(x - self.view_surface_rect.x, y - self.view_surface_rect.y)
            # update the status for the information panel
            self.status = f'X:{x_coord}, Y:{y_coord}'
        else:
            # not inside the surface rect
            self.status = "N/A"

    def check_win(self):
        # if all the pickup items are in the same cell then the game is won
        matched = True
        last_item = None
        objects = self.map_manager.domain.objects('pickups')
        # if the avatar has an item in their inventory then include it
        if self.map_manager.avatar.inventory != None:
            objects.append(self.map_manager.avatar.inventory)
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

    def draw_info_panel(self, total_time, fps):
        # calculate divisions of total_time
        seconds = total_time % (24 * 3600)
        hours = int(seconds / 3600)
        seconds %= 3600
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        # gather information into text strings
        cycle = f'Cycle: {self.cycle}'
        time = f'Time: {hours}h {minutes}m {seconds}s'
        fps = f'FPS: {int(round(fps))}'
        # draw frame
        self.information_frame.draw()
        # layout coordinates
        x_pos, y_pos, _, _ = self.information_frame.rect
        # draw each text line onto the screen
        self.screen.blit(render(cycle), (x_pos + 3, y_pos + padding(0)))
        self.screen.blit(render(time), (x_pos + 3, y_pos + padding(1)))
        self.screen.blit(render(fps), (x_pos + 3, y_pos + padding(2)))
        # status is constantly updated in the event handler
        self.screen.blit(render(self.status), (x_pos + 3, y_pos + padding(3)))

    def draw_mouse(self):
        # draw mouse cursor
        if self.panning:
            # draw the panning cursor
            self.screen.set_clip(self.view_surface_rect)
            self.screen.blit(self.cursor_panning_image,
                             (self.pan_hold_position[0] - 7, self.pan_hold_position[1] - 7))
            self.screen.set_clip(None)
        else:
            x, y = pygame.mouse.get_pos()
            # is the mouse in the view rect?
            if self.view_surface_rect.collidepoint(x, y):
                # draw normal cursor
                self.screen.set_clip(self.view_surface_rect)
                self.screen.blit(self.cursor_normal_image, (x - 7, y - 7))
                self.screen.set_clip(None)
            else:
                # outside of view surface rect, draw interface cursor
                self.screen.blit(self.cursor_interface_image, (x - 6, y))

if __name__ == '__main__':
    Main().run()
