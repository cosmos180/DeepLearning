# #  Copyright (c) 2020. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
# #  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
# #  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
# #  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
# #  Vestibulum commodo. Ut rhoncus gravida arcu.
# Libs = ["bin", "dnvqe", "hdmi", "hi_cipher", "hifisheyecarate", "isp", "ive", "md", "mpi", "nnie", "securec", "sns_gc2053",
#     "sns_imx307_2l", "sns_imx307", "sns_imx327_2l", "sns_imx327", "sns_imx335", "sns_imx415", "sns_imx458", "sns_mn34220",
#     "sns_os04b10", "sns_os05a", "sns_os08a10", "sns_ov12870", "sns_sc4210", "svpruntime", "tde", "upvqe", "VoiceEngine"]
# LibsWithUnderscore = ["hiae", "hiawb_natura", "hiawb", "hicalcflicker", "hidehaze", "hidrc", "hildci"]
#
# LibsWithStatic = Libs + LibsWithUnderscore
# AllLibs = LibsWithStatic
#
# options = {"with_{}".format(lib): [True, False] for lib in AllLibs}
# print(options)
#
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np


def yuv2bgr(filename, height, width, startfrm):
 """
 :param filename: 待处理 YUV 视频的名字
 :param height: YUV 视频中图像的高
 :param width: YUV 视频中图像的宽
 :param startfrm: 起始帧
 :return: None
 """
 fp = open(filename, "rb")

 framesize = height * width * 3 // 2 # 一帧图像所含的像素个数
 h_h = height // 2
 h_w = width // 2

 fp.seek(0, 2) # 设置文件指针到文件流的尾部
 ps = fp.tell() # 当前文件指针位置
 numfrm = ps // framesize # 计算输出帧数
 fp.seek(framesize * startfrm, 0)

 for i in range(numfrm - startfrm):
  Yt = np.zeros(shape=(height, width), dtype="uint8", order="C")
  Ut = np.zeros(shape=(h_h, h_w), dtype="uint8", order="C")
  Vt = np.zeros(shape=(h_h, h_w), dtype="uint8", order="C")

  for m in range(height):
   for n in range(width):
    Yt[m, n] = ord(fp.read(1))
  for m in range(h_h):
   for n in range(h_w):
    Ut[m, n] = ord(fp.read(1))
  for m in range(h_h):
   for n in range(h_w):
    Vt[m, n] = ord(fp.read(1))

  img = np.concatenate((Yt.reshape(-1), Ut.reshape(-1), Vt.reshape(-1)))
  img = img.reshape((height * 3 // 2, width)).astype("uint8") # YUV 的存储格式为：NV12（YYYY UV）

  # 由于 opencv 不能直接读取 YUV 格式的文件, 所以要转换一下格式
  bgr_img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_NV12) # 注意 YUV 的存储格式
  cv2.imwrite("yuv2bgr/%d.jpg" % (i + 1), bgr_img)
  print("Extract frame %d " % (i + 1))

 fp.close()
 print("job done!")
 return None


if __name__ == "__main__":
 _ = yuv2bgr(filename="xxx.yuv", height=1080, width=1920, startfrm=0)