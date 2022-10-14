//
//  cpp_mplest.cpp
//  test
//
//  Created by bughero on 2019/3/21.
//  Copyright © 2019 候 金鑫. All rights reserved.
//
#include "cpp_molest.h"

#include <iostream>
#include <mm_malloc.h>
//#define _GNU_SOURCE
//#include <sched.h>

#include <stdlib.h>

using namespace std;

namespace CPPMolest {
    template <typename TimeUnit = std::chrono::milliseconds, bool EnableAutoPrint = true>
    struct BenchmarkTimer {
        explicit BenchmarkTimer(const char *tag = "CPPMolest")
        : mTag(tag),
        mBegin(std::chrono::system_clock::now()) {
        }
        
        ~BenchmarkTimer() {
            if(EnableAutoPrint) {
                auto end = std::chrono::system_clock::now();
                cout << "[" << mTag << " cost " << std::chrono::duration_cast<TimeUnit>(end - mBegin).count() << "]";
            }
        }
        
        long long tap() {
            auto end = std::chrono::system_clock::now();
            return std::chrono::duration_cast<TimeUnit>(end - mBegin).count();
        }        

        std::string mTag;
        std::chrono::system_clock::time_point mBegin;
        std::chrono::system_clock::time_point mEnd;
//        bool mAutoPrint = true;
    };
    
    void molest_pointer_const_pointer() {
        char pointerS = 's';
        char pointerB = 'b';
        
        /*
         "所指内容不可变"
         */
        const char *SPtr = &pointerS;
        //        *SPtr = 'c';
        
        SPtr = &pointerB;
        
        
        /*
         "指向的地址不可变"
         */
        char * const BPtr = &pointerB;
        //        BPtr = &pointerS;
        
        pointerB = 's';
        
        
        cout << "SPtr value = " << *SPtr << endl;
        cout << "BPtr value = " << *BPtr << endl;
    }
    
    void molest_reinterpret_cast() {
        int num = 0x00636261;//用16进制表示32位int，0x61是字符'a'的ASCII码
        int * pnum = &num;
        char * pstr = reinterpret_cast<char *>(pnum);
        cout<<"pnum指针的值: "<<pnum<<endl;
        cout<<"pstr指针的值: "<<static_cast<void *>(pstr)<<endl;//直接输出pstr会输出其指向的字符串，这里的类型转换是为了保证输出pstr的值
        cout<<"pnum指向的内容: "<<dec<<*pnum<<endl;
        cout<<"pstr指向的内容: "<<pstr<<endl;
    }
    
#define CopyAlign4KB
    void molest_memcpy() {
        constexpr int kCoreIndex = 2;
        constexpr int kCountNumber = 10000;
        constexpr int kTotalSize = 0x60000000;
        
        char *srcPtr = nullptr, *tmpSrcPtr = nullptr, *dstPrt = nullptr, *tmpDstPtr = nullptr;
        srcPtr = new char[kTotalSize];
        dstPrt = new char[kTotalSize];
        
        
        if (kCoreIndex > 0) {
//            cpu_set_t mask;
        }
        
        int count = 0, tmp = 0, size = 65536;
        for (int k=0; k<8; k++) {
            
            count = 0;
            BenchmarkTimer<std::chrono::microseconds, false> timer;
            for (int i=0; i<kCountNumber; i++) {
                tmp = size / 4096;
                tmpSrcPtr = srcPtr;
                tmpDstPtr = dstPrt;
                
                
#ifdef CopyAlign4KB
                
                for (int j=0; j<tmp; j++) {
                    memcpy(tmpDstPtr, tmpSrcPtr, 4096);
                    tmpDstPtr += 4096;
                    tmpSrcPtr += 4096;
                }
#else
                memcpy(tmpDstPtr, tmpSrcPtr, size);
#endif
            }
            
            auto totalCost = timer.tap();
            printf("CLOCK_MONOTONIC reports %.2f us for copy %d times %d KB\n", (1.0 * totalCost)/kCountNumber, kCountNumber, size / 1024);
            
            size = size << 1;
        }
        
        delete [] srcPtr;
        srcPtr = nullptr;
        
        delete [] dstPrt;
        dstPrt = nullptr;
    }

    template<class T, class Enable = void>
    class A{};
    
    template<class T>
    class A<T, typename std::enable_if<std::is_floating_point<T>::valye>::type> {};
    
    void molest_enable_if() {
        A<double> a;
        A<int> b;
    }
    
}

