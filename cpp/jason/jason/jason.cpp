/*
 * @Author: bughero jinxinhou@tuputech.com
 * @Date: 2023-09-13 12:02:14
 * @LastEditors: bughero jinxinhou@tuputech.com
 * @LastEditTime: 2023-09-13 12:05:08
 * @FilePath: /DeepLearning/cpp/jason/jason/jason.cpp
 * @Description:
 *
 * Copyright (c) 2023 by 图普科技, All Rights Reserved.
 */
#include <cstdint>
#include <stdio.h>

namespace JASON {
    namespace CPP {}

    namespace Linux {
        int32_t __attribute__((weak)) epollTest() {
            printf("[%s]: 1 - called.\n", __FUNCTION__);
            return 0;
        }
    } // namespace Linux

} // namespace JASON