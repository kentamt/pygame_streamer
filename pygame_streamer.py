# Pygame --> Numpy --> FFMPEG pipeline --> HLS
# tested on Ubuntu20.04, python 3.9.13
# 20220802
# Kentamt

import time
from multiprocessing import Process, Queue
import subprocess as sp
import numpy as np
import pygame


class PygameStreamer():
    def __init__(self, w, h, fps,
                 bitrate='10000k',
                 speed_option='ultrafast',
                 format='hls',
                 chunk_time=1,
                 sdp_name='pygame_streamer.sdp',
                 output='./hls/live.m3u8'
                 ):

        self.image_queue = Queue()

        self._previous_data = None

        self._w = w
        self._h = h
        self._bitrate = bitrate
        self._speed_option = speed_option
        self._fps = str(fps)
        self._format = format
        self._output = None
        self._output = output

        # For hls options
        self._chunk_time = str(chunk_time)

        # For dash options
        self._remove_at_exit = str(1)

        # For rtp options
        self._sdp_name = sdp_name

        # subprocess for ffmpeg
        self._writing_process = None

        self._async_write_proc = Process(target=self.async_write, args=(self.image_queue,))
        self._async_write_proc.start()

    def __exit__(self):
        self._writing_process.stdin.close()
        self._writing_process.kill()
        self._async_write_proc.kill()

    def __init_process(self):
        if self._format == 'hls':
            command = ['ffmpeg',
                       # ----------- input --------------------
                       '-y',
                       '-f', 'rawvideo',
                       '-vcodec', 'rawvideo',
                       '-pix_fmt', 'bgr24',
                       '-s', f'{self._w}x{self._h}',
                       '-r', self._fps,
                       '-i', '-',  # input from stdin
                       # ----------- output --------------------
                       '-c:v', 'libx264',
                       '-pix_fmt', "yuv420p",
                       '-preset', self._speed_option,
                       '-b:v', self._bitrate,
                       '-hls_time', self._chunk_time,
                       '-hls_flags', "delete_segments",
                       '-force_key_frames', "expr:gte(t,n_forced*1)",
                       '-f', self._format,
                       self._output]

        elif self._format == 'dash':
            # self._output = '/dev/shm/dash/live.mpd'
            command = ['ffmpeg',
                       # ----------- input --------------------
                       '-y',
                       '-f', 'rawvideo',
                       '-vcodec', 'rawvideo',
                       '-pix_fmt', 'bgr24',
                       '-s', f'{self._w}x{self._h}',
                       '-r', self._fps,
                       '-i', '-',  # input from stdin
                       # ----------- output --------------------
                       '-c:v', 'libx264',
                       '-pix_fmt', "yuv420p",
                       '-preset', self._speed_option,
                       '-b:v', self._bitrate,
                       '-force_key_frames', "expr:gte(t,n_forced*1)",
                       '-seg_duration', self._chunk_time,
                       '-use_timeline', '1',
                       '-use_template', '1',
                       '-remove_at_exit', self._remove_at_exit,
                       '-f', self._format,
                       self._output]

        elif self._format == 'rtp':
            # self._output = f'rtp://239.0.0.1:50004' # multicast
            command = ['ffmpeg',
                       # ----------- input --------------------
                       '-y',
                       '-f', 'rawvideo',
                       '-vcodec', 'rawvideo',
                       '-pix_fmt', 'bgr24',
                       '-s', f'{self._w}x{self._h}',
                       '-r', self._fps,
                       '-i', '-',  # input from stdin
                       # ----------- output --------------------
                       '-c:v', 'libx264',
                       '-pix_fmt', "yuv420p",
                       '-preset', self._speed_option,
                       '-b:v', self._bitrate,
                       '-sdp_file', self._sdp_name,
                       '-f', self._format,
                       self._output]
        else:
            raise Exception("Sorry, unknown format. Use hls, dash or rtp.")

        self._writing_process = sp.Popen(command, stdin=sp.PIPE)
        # self._writing_process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT, stdin=sp.PIPE)


    def pygame_to_image(self, screen):
        array_data: np.array = pygame.surfarray.array3d(screen)
        array_data = array_data.astype(np.uint8)
        array_data = array_data.swapaxes(0, 1)
        array_data = array_data[..., [2, 1, 0]].copy()  # RGB2BGR
        return array_data

    def async_write(self, q: Queue):

        self.__init_process()
        sleep_sec = 0.92 / float(self._fps)
        while True:
            if not self.image_queue.empty():
                while not self.image_queue.empty():
                    array_data = self.image_queue.get()
                    self._writing_process.stdin.write(array_data.tobytes())
                    self._previous_data = array_data # TODO: check if deepcopy is needed
                    time.sleep(sleep_sec)
            else:
                if self._previous_data is not None:
                    self._writing_process.stdin.write(self._previous_data.tobytes())
                    time.sleep(sleep_sec)
