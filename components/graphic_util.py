import pygame

# domain is composed of both a map surface and an agent group
# together those are "domain".  domain = map + agents
def draw_domain(destination_surface, view_centre, renderer, group):
    # update the desired centre of the viewport
    renderer.center(view_centre)
    # if horizontal out-of-bounds limit them
    if renderer.view_rect.left < renderer.map_rect.left:
        view_centre[0] = renderer.view_rect.width / 2.0
    elif renderer.view_rect.right > renderer.map_rect.right:
        view_centre[0] = renderer.map_rect.right - (renderer.view_rect.width / 2.0)
    # if smaller than horizontal screen size then centre
    if destination_surface.get_width() <= renderer.view_rect.width:
        screen_centre_x = destination_surface.get_rect().centerx
        map_centre_x = renderer.map_rect.centerx
        view_centre[0] = screen_centre_x - (screen_centre_x - map_centre_x)
    # if vertical out-of-bounds limit them
    if renderer.view_rect.top < renderer.map_rect.top:
        view_centre[1] = renderer.view_rect.height / 2.0
    elif renderer.view_rect.bottom > renderer.map_rect.bottom:
        view_centre[1] = renderer.map_rect.bottom - (renderer.view_rect.height / 2.0)
    # if smaller than vertical screensize then centre
    if destination_surface.get_height() <= renderer.view_rect.height:
        screen_centre_y = destination_surface.get_rect().centery
        map_centre_y = renderer.map_rect.centery
        view_centre[1] = screen_centre_y - (screen_centre_y - map_centre_y)
    # align view centre to pixel coordinates by converting them to ints
    view_centre[0], view_centre[1] = int(view_centre[0]), int(view_centre[1])
    # reupdate the viewport, viewport is updated here in case the bounds were modified
    renderer.center(view_centre)
    # draw map data on surface
    renderer.draw(destination_surface, destination_surface.get_rect())
    # draw group to surface
    group.draw(destination_surface)

# draw a graphical panel showing various information
def draw_info_panel(screen, font, cycle, total_time, fps):
    screen_size = screen.get_rect()
    x, y = screen_size.right - 185, 5
    w, h = 180, 57
    seconds = total_time % (24 * 3600)
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    pygame.draw.rect(screen, (50, 50, 200), (x + 1, y + 1, w - 1, h - 1), 0)
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 1)
    text = f'Cycle: {cycle}'
    screen.blit(font.render(text, True, (200, 200, 255)), (x + 3, y + 3))
    text = f'Time: {hours}h {minutes}m {seconds}s'
    screen.blit(font.render(text, True, (200, 200, 255)), (x + 3, y + 21))
    text = f'FPS: {int(round(fps))}'
    screen.blit(font.render(text, True, (200, 200, 255)), (x + 3, y + 39))
