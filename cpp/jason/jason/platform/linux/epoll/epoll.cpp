/*
 * @Author: bughero jinxinhou@tuputech.com
 * @Date: 2023-09-13 11:57:42
 * @LastEditors: bughero jinxinhou@tuputech.com
 * @LastEditTime: 2023-09-13 12:16:02
 * @FilePath: /DeepLearning/cpp/jason/jason/platform/linux/epoll/epoll.cpp
 * @Description:
 *
 * Copyright (c) 2023 by 图普科技, All Rights Reserved.
 */
#include <stdio.h>
#include <sys/epoll.h>
#include <unistd.h>

namespace JASON {
    namespace Linux {
        int32_t epollTest() {
            printf("[%s]: 2 - called.\n", __FUNCTION__);

            int epollfd = epoll_create(1);
            if (epollfd < 0) {
                perror("epoll_create");
                return -1;
            }

            struct epoll_event ev;
            ev.events = EPOLLIN | EPOLLET;
            ev.data.fd = 0;

            if (epoll_ctl(epollfd, EPOLL_CTL_ADD, 0, &ev) < 0) {
                perror("epoll_ctl");
                return -1;
            }

            while (1) {
                struct epoll_event events[1];
                int nfds = epoll_wait(epollfd, events, 1, -1);
                if (nfds < 0) {
                    perror("epoll_wait");
                    return -1;
                }

                if (events[0].events & EPOLLIN) {
                    char buf[1024] = { 0 };
                    int len = read(0, buf, sizeof(buf));
                    if (len > 0) {
                        printf("[EPOLL]: %s\n", buf);
                    }
                }
            }

            return 0;
        }
    } // namespace Linux

} // namespace JASON