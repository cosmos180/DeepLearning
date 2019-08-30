//
//  multithread_memory_model.cpp
//  test
//
//  Created by bug小英雄 on 2018/1/4.
//  Copyright © 2018年 候 金鑫. All rights reserved.
//

#include "multithread_memory_model.hpp"
#include <atomic>
#include <stdio.h>
#include <string>
#include <assert.h>

using namespace std;

namespace Dabiq {
    
    std::atomic<std::string*> ptr;
    int data;
    
    void CPlusPlusMultiThreadMemoryModel::memory_order_acquire_consumer() {
        std::string* p = new std::string("Hello");          // A
        data = 42;                          // B
        ptr.store(p, std::memory_order_release);            // C
    }
    
    void CPlusPlusMultiThreadMemoryModel::memory_order_release_producer() {
        std::string* p2;
        while (!(p2 = ptr.load(std::memory_order_acquire)))         // D
            ;
        assert(*p2 == "Hello");                 // E
        assert(data == 42);                     // F
    }
    
    void CPlusPlusMultiThreadMemoryModel::memory_order_consume_consumer() {
        std::string* p2;
        while (!(p2 = ptr.load(std::memory_order_consume)))    // D
            ;
        assert(*p2 == "Hello");                 // E
        assert(data == 42);                     // F
    }
    
    void CPlusPlusMultiThreadMemoryModel::print_result() {
        
    }
    
}
