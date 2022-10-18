/*
 * @Author: houjinxin
 * @Date: 2022-10-14 12:04:49
 * @Last Modified by: houjinxin
 * @Last Modified time: 2022-10-14 17:37:27
 */
#ifndef AIR_THREAD_SAFE_QUEUE_H
#define AIR_THREAD_SAFE_QUEUE_H
#include <stdio.h>
#include <thread>

#include "air_base.h"
#include "base/TPThreadSafeQueue.h"

class AIR_THREAD_SAFE_QUEUE : public AIR_BASE {
  protected:
    void doTest() {
        printf("I am AIR_THREAD_SAFE_QUEUE.\n");
        std::thread producer1(&AIR_THREAD_SAFE_QUEUE::producer, this, 0, 10);
        std::thread producer2(&AIR_THREAD_SAFE_QUEUE::producer, this, 10, 20);
        std::thread producer3(&AIR_THREAD_SAFE_QUEUE::producer, this, 20, 30);
        std::thread consumer1(&AIR_THREAD_SAFE_QUEUE::consumer, this, 20);
        std::thread consumer2(&AIR_THREAD_SAFE_QUEUE::consumer, this, 10);

        producer1.join();
        producer2.join();
        producer3.join();
        consumer1.join();
        consumer2.join();
    }

    void producer(int start, int end) {
        for (int x = start; x < end; x++) {
            std::this_thread::sleep_for(std::chrono::milliseconds(200));
            { msgQueue.push(x); }
            printf("Produce message %d\n", x);
        }
    }

    void consumer(int demand) {
        while (true) {
            auto value = msgQueue.wait_and_pop();
            printf("Consume message %d\n", value);
            --demand;
            if (!demand)
                break;
        }
    }

  private:
    TupuIPC::TPThreadSafeQueue<int> msgQueue;
};

#endif