#
# Pygame --> Numpy --> FFMPEG pipeline --> HLS
# tested on Ubuntu20.04, python 3.9.13
# 20220802
# Kentamt

import subprocess as sp
import numpy as np
import pygame


class PygameStreamer():
    def __init__(self, w, h, input_fps,
                 bitrate='10000k',
                 speed_option='ultrafast',
                 format='hls', hls_time=1):
        self._w = w
        self._h = h
        self._bitrate = bitrate
        self._speed_option = speed_option
        self._input_fps = str(input_fps)
        self._format = format
        self._hls_time = str(hls_time)

        # start subprocess
        self._writing_process = None
        self.__init_process()

    def __exit__(self):
        self._writing_process.stdin.close()
        self._writing_process.kill()

    def __init_process(self):
        command = ['ffmpeg',
                   # ----------- input --------------------
                   '-y',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-s', f'{self._w}x{self._h}',
                   '-r', self._input_fps,
                   '-i', '-',  # input from stdin
                   # ----------- output --------------------
                   '-c:v', 'libx264',
                   '-pix_fmt', "yuv420p",
                   '-preset', self._speed_option,
                   '-b:v', self._bitrate,
                   '-hls_time', self._hls_time,
                   '-hls_flags', "delete_segments",
                   '-force_key_frames', "expr:gte(t,n_forced*1)",
                   '-f', self._format,
                   '/var/www/html/hls/live.m3u8']

        self._writing_process = sp.Popen(command, stdin=sp.PIPE)

    def write(self, screen):
        array_data: np.array = pygame.surfarray.array3d(screen)
        array_data = array_data.astype(np.uint8)
        array_data = array_data.swapaxes(0, 1)
        array_data = array_data[..., [2, 1, 0]].copy() # RGB2BGR
        self._writing_process.stdin.write(array_data.tobytes())
