import time, pygame
from components.utility import image_resource, file_resource, draw_info_panel, draw_domain
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from components.bundled.pyscroll.orthographic import BufferedRenderer
from components.bundled.pyscroll.group import PyscrollGroup
from components.bundled.pyscroll.data import TiledMapData
from components.mapobject import MapObject
from components.agentobject import AgentObject
from components.itemobject import ItemObject
from components.avatarobject import AvatarObject
from pygame import Rect
from components.bundled.pytmx.util_pygame import load_pygame

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
        pygame.display.set_icon(image_resource('icon.png'))
        # hide system mouse pointer
        pygame.mouse.set_visible(False)
        # load a default font
        self.font = pygame.font.Font(pygame.font.get_default_font(), 16)
        # load images for custom mouse pointers
        self.cursor_normal_image = image_resource('cursors', 'cursor_normal_x7_y7.png')
        self.cursor_panning_image = image_resource('cursors', 'cursor_pan_x7_y7.png')
        self.cursor_interface_image = image_resource('cursors', 'cursor_interface_x6_y0.png')
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
        # create a group which will render the map and map objects
        self.domain = PyscrollGroup(self.renderer)
        # lists of items and agents
        self.item_objects, self.agent_objects = [], []
        # share item_objects and the domain with the agent objects
        AgentObject.item_objects = self.item_objects
        AgentObject.domain = self.domain
        # create items
        for _ in range(30):
            # instantiate an item
            item_object = ItemObject()
            item_object._layer = 1
            # track the item
            self.item_objects.append(item_object)
            # add it to the domain
            self.domain.add(item_object)
        # create agents
        for _ in range(3):
            # instantiate an agent
            agent_object = AgentObject()
            agent_object._layer = 2
            # track the agent
            self.agent_objects.append(agent_object)
            # add it to the domain
            self.domain.add(agent_object)
        # create a player avatar and add it to the domain
        self.avatar = AvatarObject()
        self.avatar._layer = 3
        self.domain.add(self.avatar)
        # cycle counter, to be used for demo recording, marking, and playback later
        self.cycle = -1
        # status for mouse coordinates in the view
        self.xy_status = 'N/A'
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
            self.update_domain(elapsed_time)
            # clear screen
            self.screen.fill((0, 128, 128))
            # draw the main viewport to the viewport surface
            draw_domain(self.view_surface, self.main_viewport, self.renderer, self.domain)
            # and copy that surface into the main screen surface
            self.screen.blit(self.view_surface, self.view_surface_rect)
            # draw a rectangle colour around it
            pygame.draw.rect(self.screen, (255, 255, 255), self.view_surface_border_rect, 1)
            # draw information panel
            draw_info_panel(self.screen, self.font, self.cycle, total_time, clock.get_fps(), self.xy_status)
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
                    # outside of view, draw interface cursor
                    self.screen.blit(self.cursor_interface_image, (x - 6, y))
            # swap screen buffers
            pygame.display.flip()
            # limit frames-per-second
            clock.tick(fps)
        # release resources
        pygame.quit()

    def pick_cell(self, x, y):

        xr = self.view_surface_rect.x
        yr = self.view_surface_rect.y

        x_pos = x - xr
        y_pos = y - yr

        partial_x = int((self.renderer.map_rect.width - self.view_surface_rect.width) / self.map.tilewidth)
        partial_y = int((self.renderer.map_rect.height - self.view_surface_rect.height) / self.map.tileheight)

        x_pos -= partial_x * self.renderer.zoom
        y_pos -= partial_y * self.renderer.zoom

        x_pos += self.centre(x_pos, self.map.tilewidth)
        y_pos += self.centre(y_pos, self.map.tileheight)

        x_lr = self.renderer.view_rect.x
        x_total = self.renderer.map_rect.width
        x_segment = self.map.tilewidth * self.renderer._real_ratio_x

        y_lr = self.renderer.view_rect.y
        y_total = self.renderer.map_rect.height
        y_segment = self.map.tileheight * self.renderer._real_ratio_y

        x_coord = self.cell(x_lr, x_pos, x_total, x_segment, self.map.tilewidth)
        y_coord = self.cell(y_lr, y_pos, y_total, y_segment, self.map.tileheight)

        self.xy_status = f'X:{int(x_coord)}, Y:{int(y_coord)}'
        return x_coord, y_coord

    def centre(self, x, size):
        size = size * self.renderer.zoom
        x = int(((x * size) - int(x * size))) + int(size / 2)
        return x

    def cell(self, lr, pos, total, segment, tile):
        period = int(total / segment)
        base_coord = int(((lr + int(tile / 2)) / tile))
        diff = int(int(pos / period) - (pos / period))
        coord = int((pos - diff) / segment)
        return base_coord + coord

    def handle_events(self):
        # handle event queue
        for event in pygame.event.get():
            # window close widget
            if event.type == QUIT:
                self.running = False
            # keys
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # quit application
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
                    x, y = pygame.mouse.get_pos()
                    # if mouse is inside the view rect
                    if self.view_surface_rect.collidepoint(x, y):
                        x_cell, y_cell = self.pick_cell(x, y)
                if event.button == 3:
                    # right button up, end panning state
                    self.panning = False
            # panning state actions
            if self.panning:
                # if the mouse is moving
                if event.type == MOUSEMOTION:
                    # move the centre of the viewport
                    x, y = pygame.mouse.get_pos()
                    self.main_viewport[0] += x - self.pan_hold_position[0]
                    self.main_viewport[1] += y - self.pan_hold_position[1]
                    pygame.mouse.set_pos(self.pan_hold_position)

    def set_zoom_index(self, index_delta):
        # clamp index inside zoom_amounts list.
        self.zoom_amounts_index = max(0, min(self.zoom_amounts_index + index_delta,
                                             len(self.zoom_amounts) - 1))
        # update state information inside the renderer
        self.renderer.zoom = self.zoom_amounts[self.zoom_amounts_index]

    def update_domain(self, elapsed_time):
        # update the agents in the group
        self.domain.update(elapsed_time)
        # check for other agent collision, the sprites group is an expensive operation
        # so is done once on its own line here
        objects = self.domain.sprites()
        for object in objects:
            # same, done once on its own line because it's an expensive operation
            other_objects = pygame.sprite.spritecollide(object, self.domain, False)
            for other_object in other_objects:
                if other_object is not object:
                    # right here for finer-collisions:
                    #     "if overlapped then per-pixel (mask-based) comparison"
                    # for overall fast collisions and then accuracy only when overlapped
                    object.overlap(other_object)
                    other_object.overlap(object)

if __name__ == '__main__':
    Main().run()
