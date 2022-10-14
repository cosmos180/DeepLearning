#  Copyright (c) 2020. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
from numpy import *
import cv2
import os
import numpy as np

screenLevels = 255.0

class VideoCaptureYUV:
    def __init__(self, filename, size):
        self.height, self.width = size
        self.f = open(filename, 'rb')
        # self.frame_len = 5281
        # self.shape = (int(self.height*1.5), self.width)

        self.frame_len = self.width * self.height * 3
        self.shape = (self.height, self.width, 3)

    def read_raw(self):
        try:
            raw = self.f.read(int(self.frame_len))
            yuv = np.frombuffer(raw, dtype=np.uint8)
            yuv = yuv.reshape(self.shape)
        except Exception as e:
            print(str(e))
            return False, None
        return True, yuv

    def read(self):
        ret, yuv = self.read_raw()
        if not ret:
            return ret, yuv
        bgr = cv2.cvtColor(yuv, cv2.COLOR_RGBA2BGR)
        # bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
        return ret, bgr
        # return ret, yuv

# def I420ToJPG(data):
#     f = open(filename, 'rb')
#     yuvImg = cv2.imread(filename, cv2.CV_8UC1)
#     rgbaImg = cv2.cvtColor(yuvImg, cv2.COLOR_YUV2BGR_I420)
#     cv2.imshow("Converted Image", rgbaImg)

    # yuvImg;


# def RGBToJPG(data):
#



def doConvert(dir):
    element = os.walk(dir)
    for path, dir_list, file_list in element:
        print(os.path.join(path, dir))
        for file in file_list:
            if "DS_Store" in file:
                continue
            filepath = os.path.join(path, file)
            filename = file.split(".")[0]
            filenameElement = filename.split("_")
            w = int(filenameElement[1])
            h = int(filenameElement[2])
            size = (w, h)
            bgr = VideoCaptureYUV(filepath, (w, h))
            ret, frame = bgr.read()
            cv2.imwrite(os.path.join(path, filename) + ".jpg", frame)
            # f = open(file, "rb")
            # rawData = f.read()
            # f.close()


if __name__ == "__main__":
    # doConvert("/Users/cosmos/Desktop/raw_pixel_debug")
    # doConvert("/Users/cosmos/Desktop/raw_pixel_yaksha_base")
    # doConvert("/Users/cosmos/Desktop/raw_pixel_sonic_base")
    # doConvert("/Users/cosmos/Desktop/raw_pixel_sonic_base_v2")
    # doConvert("/Users/cosmos/Desktop/mask_raw_pixel")
    doConvert("/Users/cosmos/Desktop/lmq_raw_pixel")
    # doConvert("/Users/cosmos/Desktop/raw_pixel_3288_sonic")
    # doConvert("/Users/cosmos/Desktop/raw_pixel_3288_yaksha")
    # doConvert("/Users/cosmos/Desktop/raw_pixel_msm8937")
    # doConvert("/Users/cosmos/Desktop/hz_raw_pixel/")