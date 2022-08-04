

# Pygame --> Numpy --> CV2 --> FFMPEG pipeline
#
# tested on Ubuntu20.04, python 3.9.13
# 20220802
# Kenta Matsui

import os
import time
import subprocess as sp


import numpy as np
import cv2  # opencv-python
import pygame
import ffmpeg  # ffmpeg-python, https://github.com/kkroening/ffmpeg-python


def main():

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    # Set up the drawing window
    w, h = 320, 240
    x, y = 50, 50
    r = 20
    screen = pygame.display.set_mode([w, h])

    # init ffmpeg process

    # video_format = 'mp4'  # you cannot use mp4 for pipe
    video_format = 'flv'
    # video_format = 'ts'

    # url = 'http://localhost:8080'
    rtmp_url = 'rtmp://localhost:1935/stream'
    http_url = 'http://localhost:8080'
    # url = 'rtp://localhost/stream'

    writing_process = (
        ffmpeg
        .input('pipe:', format='rawvideo', codec="rawvideo", pix_fmt='bgr24', s='{}x{}'.format(w, h))
        .output(
            http_url,
            pix_fmt="yuv420p",
            vcodec="libx264",  # use same codecs of the original video
            listen=1,  # enables HTTP server
            movflags='frag_keyframe+empty_moov',
            # movflags='frag_keyframe',
            # movflags='empty_moov',
            preset="veryfast",
            max_muxing_queue_size=512,
            f=video_format)
        # .global_args("-re")  # argument to act as a live stream
        .run_async(pipe_stdin=True)
    )

    # ffplay_process = sp.Popen(['ffplay', url])

    running = True
    while running:

        # pygame part-------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        _x = np.random.randint(w, size=100)
        _y = np.random.randint(h, size=100)
        _s = np.random.randint(8, size=100)
        for __x, __y, __s in zip(_x, _y, _s):
            pygame.draw.circle(screen, (50, 255, 100), (__x, __y), __s)

        pygame.draw.circle(screen, (0, 0, 255), (x, y), r)
        pygame.display.flip()

        # move circle
        x += 10
        if x > w + r:
            x = -r

        # numpy and opencv part-------------------------------------------------

        array_data: np.array = pygame.surfarray.array3d(screen)
        array_data = array_data.astype(np.uint8)
        array_data = array_data.swapaxes(0, 1)
        array_data_bgr = cv2.cvtColor(array_data, cv2.COLOR_RGB2BGR)

        # show array data using cv2
        # cv2.imshow('screen', array_data_bgr)
        # cv2.waitKey(10)

        # FFMPEG part-----------------------------------------------------------

        # input array_data as byte data via stdin
        # writing_process.stdin.write(array_data.tobytes())
        writing_process.stdin.write(array_data_bgr.tobytes())
        pygame.time.wait(100)

    pygame.quit()
    writing_process.stdin.close()
    writing_process.wait()

    # writing_process.kill()
    ffplay_process.kill()


if __name__ == '__main__':
    main()
    print('EOP')
