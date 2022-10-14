/*
 * @Author: houjinxin
 * @Date: 2022-10-14 12:04:49
 * @Last Modified by: houjinxin
 * @Last Modified time: 2022-10-14 12:14:54
 */
#ifndef AIR_THREAD_SAFE_QUEUE_H
#define AIR_THREAD_SAFE_QUEUE_H
#include <stdio.h>

#include "air_base.h"
#include "base/TPThreadSafeQueue.h"

class AIR_THREAD_SAFE_QUEUE : public AIR_BASE {
  protected:
    void doTest() { printf("I am AIR_THREAD_SAFE_QUEUE.\n"); }
};

#endif