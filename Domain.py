class Main:
    def __init__(self):
        # - Each index value in tile_gid is a gid, then the indexes can be named:
        #     EMPTY, WALL, FLOOR = 0, 1, 2
        #     which can be used with tile_gid, like 'tile_gid[FLOOR]'
        # - gid values are defined once right here, if map data changes only here needs to be changed
        tile_gid = (0, 1, 2)
        # initialize pygame
        import pygame
        pygame.init()
        # create main window surface
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
        # dimensions of the viewport
        view_xpos, view_ypos, view_width, view_height = 10, 10, 1680, 1060
        # area for gui elements
        gui_xpos = view_xpos + view_width + 10
        gui_width = 1920 - gui_xpos - 10
        # bring in reference
        from components import utility
        # set the default font for utility functions
        utility.font_size = 16
        utility.font_object = pygame.font.Font(pygame.font.get_default_font(), utility.font_size)
        # padding function from utility
        from components.utility import padding
        # create a frame for the information panel
        information_frame_rect = pygame.Rect(gui_xpos, 10, gui_width, padding(3))
        # set up the floor group buttons
        self.floor_group = {}
        floor_select_size = 20
        from components.gui.label import Label
        floor_label = Label(self.screen, (gui_xpos, information_frame_rect.bottom + 3), 'Floor: ')
        from components.gui.pushbuttongroup import PushButtonGroup
        floor_1_button_rect = pygame.Rect(gui_xpos + floor_label.rect.width + 1, information_frame_rect.bottom + 2, floor_select_size, floor_select_size)
        self.floor_group['0'] = PushButtonGroup(self.screen, 'floor1', floor_1_button_rect, '1', 'floors', True)
        floor_2_button_rect = pygame.Rect(gui_xpos + + floor_label.rect.width + 1 + floor_select_size + 1, information_frame_rect.bottom + 2, floor_select_size, floor_select_size)
        self.floor_group['1'] = PushButtonGroup(self.screen, 'floor2', floor_2_button_rect, '2', 'floors', False)
        # bring in references so that class variables can be set
        from components.domain.domainmanager import DomainManager
        from components.object.domainobject import DomainObject
        # give the domain manager a referece to the floor group
        DomainManager.floor_group = self.floor_group
        # give both the domain manager and domain objects the tile_gid tuple
        DomainManager.tile_gid = tile_gid
        DomainObject.tile_gid = tile_gid
        # set window caption
        pygame.display.set_caption('Domain')
        # hide system mouse pointer
        pygame.mouse.set_visible(False)
        # set window icon
        pygame.display.set_icon(utility.image_alpha('icon.png'))
        # load images for custom mouse pointers
        self.cursor_domain_image = utility.image_alpha('cursors', 'cursor_domain.png')
        self.cursor_interface_image = utility.image_alpha('cursors', 'cursor_interface.png')
        # create a surface of that size for rendering
        self.view_surface = pygame.Surface((view_width, view_height)).convert()
        # create a collision rect for the surface size for interface logic
        self.view_surface_rect = pygame.Rect(view_xpos, view_ypos, view_width, view_height)
        # create a rect that outlines view_surface_rect
        self.view_surface_outline_rect = pygame.Rect(view_xpos - 1, view_ypos - 1, view_width + 2, view_height + 2)
        # create domain manager
        self.domain_manager = DomainManager(self.view_surface)
        # give domain objects a reference to the domain manager
        DomainObject.domain_manager = self.domain_manager
        # bring in reference
        from components.gui.guimanager import GuiManager
        # instantiate a gui manager
        self.gui_manager = GuiManager()
        # give domain objects a reference to the gui
        DomainObject.gui_manager = self.gui_manager
        # needed gui widgets
        from components.gui.frame import Frame
        from components.gui.button import Button
        # create information frame
        self.information_frame = Frame(self.screen, 'info_frame', information_frame_rect)
        # create buttons and add them to gui context widgets lists
        button_width, button_height = int(gui_width / 2), 20
        button_exit_rect = pygame.Rect(gui_xpos + button_width, self.view_surface_rect.bottom - button_height,
                                       button_width, button_height)
        exit_button = Button(self.screen, 'exit', button_exit_rect, 'Exit')
        button_rect = pygame.Rect(gui_xpos, floor_1_button_rect.bottom + 2, button_width, button_height)
        # pickup button context
        self.gui_manager.add_widget('pickup_context', Button(self.screen, 'pick_up', button_rect, 'Pick Up'))
        self.gui_manager.add_widget('pickup_context', exit_button)
        # putdown button context
        self.gui_manager.add_widget('putdown_context', Button(self.screen, 'put_down', button_rect, 'Put Down'))
        self.gui_manager.add_widget('putdown_context', exit_button)
        # game won context
        self.gui_manager.add_widget('win_context', Button(self.screen, 'won', button_rect, 'Won!'))
        # default context
        self.gui_manager.add_widget('default', exit_button)
        # add the floor group controls to all contexts
        for context in ('pickup_context', 'putdown_context', 'win_context', 'default'):
            self.gui_manager.add_widget(context, floor_label)
            self.gui_manager.add_widget(context, self.floor_group['0'])
            self.gui_manager.add_widget(context, self.floor_group['1'])
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
        # is the game won flag
        self.won = False
        # cycle counter
        self.cycle = -1
        # Set the state of the application to "running"
        self.running = True

    def run(self):
        from components.gui.guimanager import colours
        import time, pygame
        # maximum frames-per-second, 0 for unlimited
        fps = 0
        # instantiate a pygame clock for frame maximum limits
        clock = pygame.time.Clock()
        # track elapsed_time with more accurate os clock
        previous_time = time.time()
        # clear main surface
        self.screen.fill(colours['background'])
        # continue while the running flag is true
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
            # if follow_state centre on avatar, after update_domain to fix jitter
            if self.follow_state:
                self.domain_manager.main_viewport = list(self.domain_manager.avatar.rect.center)
            # draw the outline around the main viewport
            pygame.draw.rect(self.screen, colours['light'], self.view_surface_outline_rect, 1)
            # draw the main viewport to the viewport surface
            self.domain_manager.draw_domain()
            # and copy that surface into the main screen surface
            self.screen.blit(self.view_surface, self.view_surface_rect)
            # draw gui widgets
            self.gui_manager.draw_widgets()
            # poll for mouse position
            x, y = pygame.mouse.get_pos()
            # mouse damage to background. tracking damage is much faster than filling entire screen
            damaged_rect = pygame.Rect(x - 6, y, 16, 16)
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
            if not self.won:
                if self.check_win():
                    # display winning screen here
                    self.gui_manager.lock_context('win_context')
                    self.won = True
        # release resources
        pygame.quit()

    def handle_events(self):
        # bring in pygame reference
        import pygame
        # used constants
        from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
        from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_1, K_2, K_F1
        # handle event queue
        for event in pygame.event.get():
            gui_event = self.gui_manager.handle_event(event)
            if gui_event != None:
                # handle gui events
                if gui_event == 'floor1':
                    self.domain_manager.switch_floor(0)
                elif gui_event == 'floor2':
                    self.domain_manager.switch_floor(1)
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
                    elif event.key in (K_1, K_2):
                        # stop following on any floor switch
                        self.follow_state = False
                        if event.key == K_1:
                            # switch to floor 1
                            self.domain_manager.switch_floor(0)
                        elif event.key == K_2:
                            # switch to floor 2
                            self.domain_manager.switch_floor(1)
                    elif event.key == K_F1:
                        # toggle whether coordinates shown are relative or absolute
                        self.coordinate_toggle = not self.coordinate_toggle
                # mouse buttons
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    # if mouse is inside the view rect
                    if self.view_surface_rect.collidepoint(x, y):
                        if event.button == 2:
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
                    if event.button == 1:
                        # left button up, which is destination point for avatar
                        x, y = event.pos
                        # if mouse is inside the view rect
                        if self.view_surface_rect.collidepoint(x, y):
                            position = self.domain_manager.pick_cell(x -self.view_surface_rect.x, y - self.view_surface_rect.y)
                            self.domain_manager.avatar.move_to(position)
                    elif event.button == 3:
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
            self.status = "N/A"

    def check_win(self):
        # if all the pickup items are in the same cell then the game is won
        matched = True
        last_item = None
        objects = self.domain_manager.object_manager.objects('pickups')
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
            if (item.coord[0] != last_item.coord[0]) or (item.coord[1] != last_item.coord[1]):
                matched = False
                break
        # if true then won
        return matched

    def draw_info_panel(self, fps):
        # bring in needed functions
        from components.utility import padding, render_text
        # gather information into text strings
        cycle = f'Cycle: {self.cycle}'
        fps = f'FPS: {int(round(fps))}'
        # draw frame
        self.information_frame.draw()
        # layout coordinates
        x_pos, y_pos, _, _ = self.information_frame.rect
        # draw each text line onto the screen
        self.screen.blit(render_text(cycle), (x_pos + 3, y_pos + padding(0)))
        self.screen.blit(render_text(fps), (x_pos + 3, y_pos + padding(1)))
        self.screen.blit(render_text(self.status), (x_pos + 3, y_pos + padding(2)))

    def draw_mouse(self, x, y):
        # draw mouse cursor
        # is the mouse in the view rect?
        if self.view_surface_rect.collidepoint(x, y):
            # draw domain cursor
            self.screen.set_clip(self.view_surface_rect)
            if self.panning_state:
                self.screen.blit(self.cursor_domain_image,
                                (self.panning_state_position[0] - 15, self.panning_state_position[1] - 15))
            else:
                self.screen.blit(self.cursor_domain_image, (x - 15, y - 15))
            self.screen.set_clip(None)
        else:
            # outside of view surface rect, draw interface cursor
            self.screen.blit(self.cursor_interface_image, (x - 6, y))

if __name__ == '__main__':
    Main().run()
