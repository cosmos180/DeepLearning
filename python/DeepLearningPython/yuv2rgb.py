#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

__author__ = "Farid Zakaria"
__copyright__ = "Copyright 2011, AMD"
__credits__ = ["Sherin Sasidhan (serin.s@gmail.com)"]
__license__ = "GPL"
__version__ = "1.0."
__maintainer__ = "Farid Zakaria"
__email__ = "farid.zakaria@amd.com"
__status__ = "Prototype"

import argparse
from PIL import Image
import sys
from struct import *
import os
import math
import cv2
import numpy as np

DEFAULT_STRIDE = -1
DEFAULT_FRAME = 0

parser = argparse.ArgumentParser(prog='YUV2RGB Converter', description='Convert YUV Raw images into RGB format')
parser.add_argument('filename', type=str)
parser.add_argument('width', type=int)
parser.add_argument('height', type=int)
parser.add_argument('--stride', default=DEFAULT_STRIDE, type=int,
                    help='stride of the image (default: width of the image')
parser.add_argument('--frame', default=DEFAULT_FRAME, type=int, help='frame number to grab (default: index 0)')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')


class Converter(object):
    """Base class that should define interface for all conversions"""

    def __init__(self, filename, width, height, stride, frame):
        self.filename = filename
        self.width = width
        self.height = height
        self.stride = stride
        self.frame = frame

    # constructor#

    def Convert():
        raise NotImplementedError("Should have implemented this!")


# convert#
# Converter#


class NV12Converter(Converter):
    """This class converts NV12 files into RGB"""

    def __init__(self, filename, width, height, stride, frame):
        super(NV12Converter, self).__init__(filename, width, height, stride, frame)

    # constructor#

    def Convert(self):
        f_y = open(self.filename, "rb")
        f_uv = open(self.filename, "rb")

        converted_image_filename = self.filename.split('.')[0] + ".jpg"
        converted_image = Image.new("RGB", (self.width, self.height))
        pixels = converted_image.load()

        size_of_file = os.path.getsize(self.filename)
        size_of_frame = ((3.0 / 2.0) * self.height * self.width)
        number_of_frames = size_of_file / size_of_frame
        frame_start = int(size_of_frame * self.frame)
        uv_start = int(frame_start + (self.width * self.height))

        # lets get our y cursor ready
        print("filename %s size_of_file %d frame_start %d width %d height %d ~" % (self.filename, size_of_file, frame_start, self.width, self.height))
        f_y.seek(frame_start)

        img = np.zeros((self.height, self.width, 3), dtype=np.int32)

        for j in range(0, self.height):
            for i in range(0, self.width):
                # uv_index starts at the end of the yframe.  The UV is 1/2 height so we multiply it by j/2
                # We need to floor i/2 to get the start of the UV byte
                uv_index = uv_start + (self.width * math.floor(j / 2)) + (math.floor(i / 2)) * 2
                f_uv.seek(uv_index)

                # print("y %s u %s v %s ~" % (f_y.read(1), f_uv.read(1), f_uv.read(1)))

                y = ord(f_y.read(1))
                u = ord(f_uv.read(1))
                v = ord(f_uv.read(1))

                b = 1.164 * (y - 16) + 2.018 * (u - 128)
                g = 1.164 * (y - 16) - 0.813 * (v - 128) - 0.391 * (u - 128)
                r = 1.164 * (y - 16) + 1.596 * (v - 128)

                pixels[i, j] = int(r), int(g), int(b)
                img[j][i] = [int(b), int(g), int(r)]
                # img[j][i] = [int(r), int(g), int(b)]

        # converted_image.save(converted_image_filename)
        cv2.imwrite(converted_image_filename, img)


def main():
    args = parser.parse_args()

    if args.stride == DEFAULT_STRIDE:
        args.stride = args.width

    if args.frame < 0:
        args.frame = 0

    converter = NV12Converter(args.filename, args.width, args.height, args.stride, args.frame)
    converter.Convert()


# main function#

if __name__ == "__main__":
    main()
