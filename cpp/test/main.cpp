//
//  main.cpp
//  test
//
//  Created by bug小英雄 on 2018/1/2.
//  Copyright © 2018年 候 金鑫. All rights reserved.
//

#include <iostream>
#include <string>
#include <thread>
#include <math.h>
#include <atomic>
#include <unistd.h>

#include "cpp_mplest.hpp"
#include "ntpd.h"

std::atomic_flag lock = ATOMIC_FLAG_INIT;

void f(int n) {
    while (lock.test_and_set()) {
        printf("Waiting.......\n");
    }
    printf("Thread %d start working...\n", n);
}

void g(int n) {
    printf("Thread %d is going to start...\n", n);
    lock.clear();
    printf("Thread %d starts working...\n", n);
    
}

int main() {
//    lock.test_and_set();
//    std::thread t1(f, 1);
//    std::thread t2(g, 2);
//
//    t1.join();
//    usleep(100);
//    t2.join();
    
//    CPPMolest::molest_reinterpret_cast();
//    CPPMolest::molest_pointer_const_pointer();
//    CPPMolest::molest_memcpy();
//    CPPMolest::molest_memory_algin();
    CPPMolest::molest_string_concat();
    
//    startNtpd();
    

    return 0;
}
