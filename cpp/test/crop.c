//
//  crop.c
//  test
//
//  Created by bug小英雄 on 2018/1/27.
//  Copyright © 2018年 候 金鑫. All rights reserved.
//

#include <stdio.h>

//void crop() {
//    for (int ii=0; ii<nCount; ii++) {
//        TPRect _tmp = targetRects.at(ii);
//        int left = _tmp.left, right = _tmp.right, top = _tmp.top, bottom = _tmp.bottom;
//        int offsetX = 0, offsetY = 0;
//        for (int h = 0; h < mnNetworkHeight; h++) {
//            offsetY = top + (bottom - top) * h / mnNetworkHeight;
//            for (int w = 0; w < mnNetworkWidth; w++) {
//                offsetX = left + (right - left) * w / mnNetworkWidth;
//                if (offsetY < 0 || offsetX < 0 || offsetY > height || offsetX > width) {
//                    input_tensor_mapped(ii, h, w, 0) = 0.0;
//                    input_tensor_mapped(ii, h, w, 1) = 0.0;
//                    input_tensor_mapped(ii, h, w, 2) = 0.0;
//                    
//                    int index = (h * mnNetworkWidth + w) * 4;
//                    mpNetworkPixelSnapshoot[index]     = 0;
//                    mpNetworkPixelSnapshoot[index + 1] = 0;
//                    mpNetworkPixelSnapshoot[index + 2] = 0;
//                    mpNetworkPixelSnapshoot[index + 3] = 255;
//                } else {
//                    const uchar *tmp = data + 4 * (width *offsetY + offsetX);
//                    input_tensor_mapped(ii, h, w, 0) = preprocess((float)tmp[2]);
//                    input_tensor_mapped(ii, h, w, 1) = preprocess((float)tmp[1]);
//                    input_tensor_mapped(ii, h, w, 2) = preprocess((float)tmp[0]);
//                    
//                    int index = (h * mnNetworkWidth + w) * 4;
//                    mpNetworkPixelSnapshoot[index]     = tmp[0];
//                    mpNetworkPixelSnapshoot[index + 1] = tmp[1];
//                    mpNetworkPixelSnapshoot[index + 2] = tmp[2];
//                    mpNetworkPixelSnapshoot[index + 3] = tmp[3];
//                }
//            }
//        }
//    }
//}

