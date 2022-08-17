

# Pygame --> Numpy --> CV2 --> FFMPEG pipeline
#
# tested on Ubuntu20.04, python 3.9.13
# 20220802
# Kentamt

import os, sys
import pygame
import numpy as np
from pygame_streamer import PygameStreamer

from multiprocessing import Process, Queue


def main():

    # if you want to test without pygame GUI, use this.
    # os.environ["SDL_VIDEODRIVER"] = "dummy"

    # Set up the drawing window
    pygame.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 15)
    w, h = 320, 240
    x, y = 0, 120
    r = 16
    pygame_fps = int(sys.argv[1])
    pygame_sleep_time = int(1.0/ pygame_fps* 1000) # [msec]
    screen = pygame.display.set_mode([w, h])

    # Set up pygame streamer
    fps = 15
    streamer = PygameStreamer(w, h, fps,
                              bitrate='10000k',
                              output='./hls/live.m3u8',
                              format='hls',
                              chunk_time=2,
                              verbose=True)
    

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

        # put an image in a queue
        image = streamer.pygame_to_image(screen)
        streamer.image_queue.put(image)

        # sleep
        pygame.time.wait(pygame_sleep_time)

        # move circle and count up
        x += 32
        if x > w + r:
            x = 0
        counter += 1

    print('terminate streamer')
    streamer.terminate()
    pygame.quit()
    print('EOP')

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
