/*
 * @Author: your name
 * @Date: 2020-10-19 10:57:52
 * @LastEditTime: 2020-10-21 11:55:33
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /conan/test_package/target/Cache.h
 */
#include <thread>
#include <chrono>
#include "include/common.h"

#define CACHE_LINE_SIZE 64
struct STest {
   alignas(CACHE_LINE_SIZE) int a;
};

struct Cache {
    template <typename type = STest>
    void func(type* Num) {
        if constexpr (std::is_same<typename std::decay<type>::type, int>::value) {
            for(int i = 0; i < 100000; i++) {
                (*Num)++;
            }       
        } else {
            for(int i = 0; i < 100000; i++) {
                Num->a++;
            }  
        }
    }

    template <typename type = int>
    int test() {
        type ArrayTest[4] = {0};
        auto start = std::chrono::steady_clock::now();
        auto t1 = std::thread(std::bind(&Cache::func<type>, this, std::placeholders::_1), &ArrayTest[0]);
        auto t2 = std::thread(std::bind(&Cache::func<type>, this, std::placeholders::_1), &ArrayTest[1]);
        auto t3 = std::thread(std::bind(&Cache::func<type>, this, std::placeholders::_1), &ArrayTest[2]);
        auto t4 = std::thread(std::bind(&Cache::func<type>, this, std::placeholders::_1), &ArrayTest[3]);

        t1.join();
        t2.join();
        t3.join();
        t4.join();
        auto end = std::chrono::steady_clock::now();
        printf("Use no align time %llu us\n", std::chrono::duration_cast<std::chrono::microseconds>(end - start).count());
        printf("Use no align time %d\n", (-1)/4);
        printf("Use no align time %d\n", (3)/4);
        printf("Use no align time %d\n", (1920+31) & ~31);
    }
};
