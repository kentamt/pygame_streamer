

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

    # os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    # Set up the drawing window
    w, h = 320, 240
    x, y = 0, 120
    r = 16
    screen = pygame.display.set_mode([w, h])

    # init ffmpeg process

    # video_format = 'mp4'  # you cannot use mp4 for pipe
    # video_format = 'flv'
    # video_format = 'ts'
    # video_format = 'mpegts'

    # url = 'http://localhost:8080'
    rtmp_url = 'rtmp://localhost:1935/stream'
    http_url = 'http://localhost:8080'
    udp_url = 'udp://239.0.0.1:1234?ttl=13'

    # writing_process = (
    #     ffmpeg
    #     .input('pipe:', format='rawvideo', codec="rawvideo", pix_fmt='bgr24', s='{}x{}'.format(w, h))
    #     .setpts('2.6*PTS')  #
    #     .output(
    #         'udp://239.0.0.1:1234?ttl=13',
    #         pix_fmt="yuv420p",
    #         vcodec="libx264",  # use same codecs of the original video
    #         listen=1,  # enables HTTP server
    #         movflags='frag_keyframe+empty_moov',
    #         preset="veryfast",
    #         max_muxing_queue_size=512,
    #         f='mp4')
    #     # .global_args("-re")  # argument to act as a live stream
    #     .run_async(pipe_stdin=True)
    # )

    # writing_process = (
    #     ffmpeg
    #     .input('pipe:', format='rawvideo', codec="rawvideo", pix_fmt='bgr24', s='{}x{}'.format(w, h))
    #     # .setpts('2.6*PTS')  #
    #     .output(
    #         'http://localhost:8080',
    #         # 'udp://239.0.0.1:1234?ttl=13',
    #         pix_fmt="yuv420p",
    #         vcodec="libx264",  # use same codecs of the original video
    #         listen=1,  # enables HTTP server
    #         movflags='frag_keyframe+empty_moov',
    #         preset="veryfast",
    #         max_muxing_queue_size=512,
    #         f='flv')
    #     .run_async(pipe_stdin=True)
    # )


    # writing_process = (
    #     ffmpeg
    #     .input('pipe:', format='rawvideo', codec="rawvideo", pix_fmt='bgr24', s='{}x{}'.format(w, h))
    #     .output(
    #         udp_url,
    #         pix_fmt="yuv420p",
    #         vcodec="libx264",
    #         preset="veryfast",
    #         f=video_format)
    #     .run_async(pipe_stdin=True)
    # )

    # writing_process = (
    #     ffmpeg
    #     .input('pipe:', format='rawvideo', codec="rawvideo", pix_fmt='bgr24', s='{}x{}'.format(w, h))
    #     .output(
    #         "rtp://239.0.0.1:50004",
    #         pix_fmt="yuv420p",
    #         vcodec="libx264",
    #         preset="veryfast",
    #         sdp_file='saved_sdp_file',
    #         f='rtp')
    #     .run_async(pipe_stdin=True)
    # )

    # HLS
    # writing_process = (
    #     ffmpeg
    #     .input('pipe:', format='rawvideo', codec="rawvideo", pix_fmt='bgr24', s='{}x{}'.format(w, h))
    #     .setpts('2.6*PTS')  # TODO: Magic number ...
    #     .output(
    #         '/var/www/html/hls/live.m3u8',
    #         pix_fmt="yuv420p",
    #         vcodec="libx264",
    #         preset="ultrafast",
    #         hls_time="1",
    #         hls_flags="delete_segments",
    #         segment_wrap="10",
    #         f='hls')
    #     .run_async(pipe_stdin=True)
    # )

    # DASH https://www.codeinsideout.com/blog/pi/stream-ffmpeg-hls-dash/#use-mpeg-dash-streaming
    # mkdir -p /dev/shm/dash
    # ln -s /dev/shm/dash /var/www/html/dash
    # writing_process = (
    #     ffmpeg
    #     .input('pipe:', format='rawvideo', codec="rawvideo", pix_fmt='bgr24', s='{}x{}'.format(w, h))
    #     .setpts('2.6*PTS')  # TODO: Magic number for 10FPS ...
    #     .output(
    #         '/dev/shm/dash/live.mpd',
    #         # v="debug",
    #         pix_fmt="yuv420p",
    #         vcodec="libx264",
    #         preset="ultrafast",
    #         video_bitrate=1000000,
    #         seg_duration=2,
    #         streaming=1,
    #         window_size=10,
    #         remove_at_exit=1,
    #         f='dash')
    #     # .global_args("-r 10")  # argument to act as a live stream
    #     .run_async(pipe_stdin=True)
    # )
    #

    dimension = '{}x{}'.format(w, h)
    f_format = 'bgr24'  # remember OpenCV uses bgr format
    # command = ['ffmpeg',
    #            '-y',
    #            '-f', 'rawvideo',
    #            '-vcodec', 'rawvideo',
    #            '-pix_fmt', 'bgr24',
    #            '-s', dimension,
    #            '-r', '9.7',
    #            # '-re',
    #            '-i', '-',
    #            # '-an',
    #            '-c:v', 'libx264',  #
    #            '-pix_fmt', "yuv420p",
    #            '-b:v', '10000k',
    #            '-preset', 'ultrafast',
    #            '-seg_duration', '2',
    #            # '-streaming', '1',
    #            '-window_size', '5',
    #            '-remove_at_exit', '1',
    #            # '-r', '10',
    #            '-f', 'dash',
    #            '/dev/shm/dash/live.mpd']



    command = ['ffmpeg',
               '-y',
               '-f', 'rawvideo',
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24',
               '-s', f'{w}x{h}',
               '-r', '9.5',
               # '-re',
               '-i', '-',
               # '-an',
               '-c:v', 'libx264',  #
               '-pix_fmt', "yuv420p",
               '-preset', 'ultrafast',
               '-b:v', '10000k',
               '-force_key_frames', "expr:gte(t,n_forced*1)",
               '-hls_time', "1",
               '-hls_flags', "delete_segments",
               # '-remove_at_exit', '1',
               # '-segment_wrap', "10",
               '-f', 'hls',
               '/var/www/html/hls/live.m3u8']

    writing_process = sp.Popen(command, stdin=sp.PIPE)

    font = pygame.font.Font(pygame.font.get_default_font(), 15)
    counter = 0
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

        text_src = font.render(f'{counter}', False, (255,255,255))
        screen.blit(text_src, (10, 10))

        pygame.display.flip()

        # numpy and opencv part-------------------------------------------------

        array_data: np.array = pygame.surfarray.array3d(screen)
        array_data = array_data.astype(np.uint8)
        array_data = array_data.swapaxes(0, 1)
        array_data = cv2.cvtColor(array_data, cv2.COLOR_RGB2BGR)
        # array_data[:,:,0], array_data[:,:,2] = array_data[:,:,2], array_data[:,:,0]

        # show array data using cv2
        # cv2.imshow('screen', array_data_bgr)
        # cv2.waitKey(10)

        # FFMPEG part-----------------------------------------------------------

        # input array_data as byte data via stdin
        writing_process.stdin.write(array_data.tobytes())
        # writing_process.stdin.write(array_data_bgr.tobytes())
        # pygame.time.wait(1)
        time.sleep(0.1)

        # move circle
        x += 32
        if x > w + r:
            x = 0
        counter += 1

    pygame.quit()
    writing_process.stdin.close()
    writing_process.kill()


if __name__ == '__main__':
    main()
    print('EOP')
