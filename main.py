

# Pygame --> Numpy --> CV2 --> FFMPEG pipeline
#
# tested on Ubuntu20.04, python 3.9.13
# 20220802
# Kentamt

import os
import time
import pygame
import numpy as np
from pygame_streamer import PygameStreamer


def main():

    # if you want to test without pygame GUI, use this.
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    pygame.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 15)

    # Set up the drawing window
    w, h = 320, 240
    x, y = 0, 120
    r = 16
    screen = pygame.display.set_mode([w, h])

    # Set up pygame streamer
    fps = 9.5  # not exact 10
    streamer = PygameStreamer(w, h, fps, bitrate='10000k', speed_option='ultrafast', format='hls', hls_time=1)

    counter = 0
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # update pygame screen
        screen.fill((0, 0, 0))
        draw_screen(counter, font, h, r, screen, w, x, y)
        pygame.display.flip()

        # stream pygame screen
        streamer.write(screen)

        # sleep
        time.sleep(0.1)

        # move circle and count up
        x += 32
        if x > w + r:
            x = 0
        counter += 1

    pygame.quit()


def draw_screen(counter, font, h, r, screen, w, x, y):

    # scatter circles
    xs = np.random.randint(w, size=100)
    ys = np.random.randint(h, size=100)
    ss = np.random.randint(8, size=100)
    for _x, _y, _s in zip(xs, ys, ss):
        pygame.draw.circle(screen, (50, 255, 100), (_x, _y), _s)

    # circle moving from left to right
    pygame.draw.circle(screen, (0, 0, 255), (x, y), r)

    # update counter
    text_src = font.render(f'{counter}', False, (255, 255, 255))
    screen.blit(text_src, (10, 10))



if __name__ == '__main__':
    main()
