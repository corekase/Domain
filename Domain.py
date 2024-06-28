import time, pygame
from pygame import Rect
from components.utility import image_alpha_resource, file_resource, padding, render
from components.bundled.pytmx.util_pygame import load_pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from components.bundled.pyscroll.orthographic import BufferedRenderer
from components.bundled.pyscroll.data import TiledMapData
from components.object.objectmanager import ObjectManager
from components.object.mapobject import MapObject
from components.object.genericobject import GenericObject
from components.object.pickupobject import PickupObject
from components.object.agentobject import AgentObject
from components.object.avatarobject import AvatarObject
from components.gui.guimanager import GuiManager
from components.gui.button import Button
from components.gui.frame import Frame
from components.gui.widget import colours
from components import utility

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
        # load the map
        self.map = load_pygame(file_resource('domains', 'domain.tmx'))
        # give MapObject subclasses a common reference to the map
        MapObject.map = self.map
        # calculate view size at 1.0 zoom
        map_graphical_width = self.map.width * self.map.tilewidth
        map_graphical_height = self.map.height * self.map.tileheight
        # create a surface of that size for rendering
        self.view_surface = pygame.Surface((map_graphical_width, map_graphical_height)).convert()
        # for that surface, centre both the x and y axis relative to the screen surface
        view_xpos = (self.screen.get_rect().width - map_graphical_width) // 2
        view_ypos = (self.screen.get_rect().height - map_graphical_height) // 2
        # create a collision rect for the surface size for interface logic
        self.view_surface_rect = Rect(view_xpos, view_ypos, map_graphical_width, map_graphical_height)
        # create a rect for a border colour around the view surface
        self.view_surface_border_rect = Rect(view_xpos - 1, view_ypos - 1, map_graphical_width + 2, map_graphical_height + 2)
        # create renderer
        self.renderer = BufferedRenderer(TiledMapData(self.map), self.view_surface.get_size(), False)
        # set initial viewport in the renderer to the center of the map, as [x, y]
        self.main_viewport = list(self.renderer.map_rect.center)
        # set the zoom levels for the renderer
        self.zoom_amounts_index = 0
        self.zoom_amounts = [1.0, 2.0, 3.0, 4.0]
        self.renderer.zoom = self.zoom_amounts[self.zoom_amounts_index]
        # state for whether or not panning the view
        self.panning = False
        # when panning lock mouse position to this position
        self.pan_hold_position = None
        # create an object manager
        self.domain = ObjectManager(self.renderer)
        # share that domain with map objects
        MapObject.domain = self.domain
        # helper function to create objects
        def populate(number, cls, layer, group):
            for _ in range(number):
                # instantiate from the class
                instance = cls()
                # set the layer, higher takes priority
                instance.layer = layer
                # add the instance to the group
                self.domain.object_add(group, instance)
        # create generic items
        populate(30, GenericObject, 1, 'generic')
        # create pickup items
        populate(3, PickupObject, 2, 'pickups')
        # create agents
        populate(4, AgentObject, 3, 'agents')
        # create a player avatar and add it to the domain
        self.avatar = AvatarObject()
        self.avatar.layer = 4
        self.domain.object_add('avatar', self.avatar)
        # cycle counter, to be used for demo recording, marking, and playback later
        self.cycle = -1
        # text status containing the x and y map indexes of the mouse position, updated in the event handler
        self.status = None
        # instantiate a GUI manager
        self.gui = GuiManager()
        # give the map object access to gui switch context
        MapObject.gui = self.gui
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
                self.update_domain(elapsed_time)
            # clear screen
            self.screen.fill(colours['background'])
            # draw the main viewport to the viewport surface
            self.draw_domain()
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
                    self.avatar.pick_up()
                elif gui_event == 'put_down':
                    self.avatar.put_down()
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
                            # right button down, begin panning state if not fully zoomed out
                            if self.zoom_amounts_index > 0:
                                self.panning = True
                                self.pan_hold_position = x, y
                        elif event.button == 4:
                            # wheel scroll up, increase zoom index
                            self.set_zoom_index(1)
                            # if right-mouse button is also pressed begin panning
                            if pygame.mouse.get_pressed()[2]:
                                self.panning = True
                                self.pan_hold_position = x, y
                        elif event.button == 5:
                            # wheel scroll down, decrease zoom index
                            self.set_zoom_index(-1)
                            # if panning is active end panning if fully zoomed out
                            if self.panning:
                                if self.zoom_amounts_index == 0:
                                    self.panning = False
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        # left button up, which is destination point for avatar
                        x, y = event.pos
                        # if mouse is inside the view rect
                        if self.view_surface_rect.collidepoint(x, y):
                            position = self.pick_cell(x, y)
                            self.avatar.move_to(position)
                    if event.button == 3:
                        # right button up, end panning state
                        self.panning = False
                # panning state actions
                if self.panning:
                    # if the mouse is moving
                    if event.type == MOUSEMOTION:
                        # move the centre of the viewport
                        x, y = event.pos
                        self.main_viewport[0] += x - self.pan_hold_position[0]
                        self.main_viewport[1] += y - self.pan_hold_position[1]
                        pygame.mouse.set_pos(self.pan_hold_position)
        # update the x and y map indexes for the information panel
        x, y = pygame.mouse.get_pos()
        if self.view_surface_rect.collidepoint(x, y):
            x_coord, y_coord = self.pick_cell(x, y)
            # update the status for the information panel
            self.status = f'X:{x_coord}, Y:{y_coord}'
        else:
            # not inside the surface rect
            self.status = "N/A"

    def update_domain(self, elapsed_time):
        # check for other mapobject collision, the sprites group is an expensive operation
        # so is done once on its own line here
        objects = self.domain.domain().sprites()
        for object in objects:
            # same, done once on its own line because it's an expensive operation
            other_objects = pygame.sprite.spritecollide(object, self.domain.domain(), False)
            for other_object in other_objects:
                if not (other_object is object):
                    # right here for finer-collisions:
                    #     "if overlapped then per-pixel (mask-based) comparison"
                    # for overall fast collisions and then accuracy only when overlapped
                    object.overlap(other_object)
                    other_object.overlap(object)
        # update all mapobjects and their subclasses in the domain group
        self.domain.domain().update(elapsed_time)

    def check_win(self):
        # if all the pickup items are in the same cell then the game is won
        matched = True
        last_item = None
        objects = self.domain.objects('pickups')
        # if the avatar has an item in their inventory then include it
        if self.avatar.inventory != None:
            objects.append(self.avatar.inventory)
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

    def pick_cell(self, x, y):
        # normalize x and y mouse position to the screen coordinates of the surface
        x_pos, y_pos = x - self.view_surface_rect.centerx, y - self.view_surface_rect.centery
        # get all the needed information from the map and renderer
        x_tile_size = self.map.tilewidth * self.renderer.zoom
        y_tile_size = self.map.tileheight * self.renderer.zoom
        map_centre_x = self.renderer.map_rect.centerx * self.renderer.zoom
        map_centre_y = self.renderer.map_rect.centery * self.renderer.zoom
        view_centre_x = self.renderer.view_rect.centerx * self.renderer.zoom
        view_centre_y = self.renderer.view_rect.centery * self.renderer.zoom
        # go through each geometry frame ending at the x and y mouse position
        relative_x = map_centre_x - view_centre_x - x_pos
        relative_y = map_centre_y - view_centre_y - y_pos
        # divide those into tile sizes to get a coordinate
        x_coord, y_coord = relative_x / x_tile_size, relative_y / y_tile_size
        # convert that screen coordinate into an array coordinate for programming
        x_coord = int(-x_coord + self.map.width / 2)
        y_coord = int(-y_coord + self.map.height / 2)
        # coordinates are now in map array indexes
        return x_coord, y_coord

    def set_zoom_index(self, index_delta):
        # clamp index inside zoom_amounts list.
        self.zoom_amounts_index = max(0, min(self.zoom_amounts_index + index_delta,
                                             len(self.zoom_amounts) - 1))
        # update state information inside the renderer
        self.renderer.zoom = self.zoom_amounts[self.zoom_amounts_index]

    def draw_domain(self):
        # update the desired centre of the viewport
        self.renderer.center(self.main_viewport)
        # if horizontal out-of-bounds limit them
        if self.renderer.view_rect.left < self.renderer.map_rect.left:
            self.main_viewport[0] = self.renderer.view_rect.width / 2.0
        elif self.renderer.view_rect.right > self.renderer.map_rect.right:
            self.main_viewport[0] = self.renderer.map_rect.right - (self.renderer.view_rect.width / 2.0)
        # if smaller than horizontal screen size then centre
        if self.view_surface.get_width() <= self.renderer.view_rect.width:
            screen_centre_x = self.view_surface.get_rect().centerx
            map_centre_x = self.renderer.map_rect.centerx
            self.main_viewport[0] = screen_centre_x - (screen_centre_x - map_centre_x)
        # if vertical out-of-bounds limit them
        if self.renderer.view_rect.top < self.renderer.map_rect.top:
            self.main_viewport[1] = self.renderer.view_rect.height / 2.0
        elif self.renderer.view_rect.bottom > self.renderer.map_rect.bottom:
            self.main_viewport[1] = self.renderer.map_rect.bottom - (self.renderer.view_rect.height / 2.0)
        # if smaller than vertical screensize then centre
        if self.view_surface.get_height() <= self.renderer.view_rect.height:
            screen_centre_y = self.view_surface.get_rect().centery
            map_centre_y = self.renderer.map_rect.centery
            self.main_viewport[1] = screen_centre_y - (screen_centre_y - map_centre_y)
        # align view centre to pixel coordinates by converting them to ints
        self.main_viewport[0], self.main_viewport[1] = int(self.main_viewport[0]), int(self.main_viewport[1])
        # reupdate the viewport, viewport is updated here in case the bounds were modified
        self.renderer.center(self.main_viewport)
        # draw map and group objects to surface
        self.domain.domain().draw(self.view_surface)

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
