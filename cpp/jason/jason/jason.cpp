/*
 * @Author: bughero jinxinhou@tuputech.com
 * @Date: 2023-09-13 12:02:14
 * @LastEditors: bughero jinxinhou@tuputech.com
 * @LastEditTime: 2023-10-26 14:23:24
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
        void hello() {
            // // 将字符串保存到显存中
            // char *string = "Hello, world!";
            // int i;
            // for (i = 0; string[i] != '\0'; i++) {
            //     *((char *)0xB8000 + i) = string[i];
            // }

            // // 设置光标位置
            // int cursor_x = 0;
            // int cursor_y = 0;
            // int10h(0x02, cursor_x, cursor_y);
        }

        int32_t __attribute__((weak)) epollTest() {
            printf("[%s]: 1 - called.\n", __FUNCTION__);
            return 0;
        }
    } // namespace Linux

} // namespace JASON