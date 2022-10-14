/*
 * @Author: your name
 * @Date: 2020-09-24 22:21:12
 * @LastEditTime: 2020-12-30 15:43:14
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /conan-zlib/test_package/target/Bitmaph
 */

#include "include/common.h"
#include <unistd.h>

/**
 * 4 bit/人 * 1024000人 / 8bit/Byte = 512000 Bytes
 */

enum BitCountOneNumber {
    OneBitOneNumber = 1,
    FourBitOneNumber = 4,
    EightBitOneNumber = 8
};

const short kDefaultMemoryFineness = sizeof(int);
constexpr uint32_t kMaxSize = 200*10000; // 200w
// constexpr uint32_t kMaxMemorySize = 4*kMaxSize/8;

template <BitCountOneNumber bitCountType>
class BitmapCounter {
public:
    explicit BitmapCounter() {
        void *allocatedBuffer = nullptr;
        int ret = -1;
        if ((ret = posix_memalign(&allocatedBuffer, sysconf(_SC_PAGESIZE), kMaxMemorySize)) == 0) {
            mpCounter = static_cast<uint8_t*>(allocatedBuffer);
        } else {
            printf("ret %d, alignment is %zu, allocating %zu byte(s)", ret, kDefaultMemoryFineness, kMaxMemorySize);
        }
        memset(mpCounter, 0, kMaxMemorySize);
    }

    ~BitmapCounter() {
        free(mpCounter);
        mpCounter = nullptr;
    }

    inline uint32_t setAndGet(uint32_t n) {
        if constexpr (bitCountType == FourBitOneNumber) {
            uint32_t base = n / 2;
            uint32_t remainder = n % 2;
            uint32_t last = (mpCounter[base] & (0xf0 >> (4*remainder))) >> ((1-remainder)*4);
            //        std::cout << "last value is " << last << "!\n";
            //        std::cout << "new value is " << last+1 << "!\n";
            if (last < 15) {
                /**
                 * one number by 4 bit, so max is 15
                 */
                if (remainder == 0) {
                    mpCounter[base] &= 0x0f;
                } else {
                    mpCounter[base] &= 0xf0;
                }

                mpCounter[base] |= (add(last, 1) << ((1-remainder)*4));
                // return (mpCounter[base] & (0xf0 >> (4*remainder))) >> ((1-remainder)*4);
                return last+1;
            } else {
                return 15;
            }
        } else if constexpr (bitCountType == OneBitOneNumber){
            auto byteIndex = n / 8;
            auto bitIndex = n % 8;
            auto data = (0x1 << (7-bitIndex));
//            std::cout << "n " << n << " byteIndex " << byteIndex << " bitIndex " << bitIndex << "data " << data << "!\n";
            auto newValue = mpCounter[byteIndex] | (0x1 << (7-bitIndex));
            mpCounter[byteIndex] = newValue;
            return newValue >> (7-bitIndex);
        } else if constexpr (bitCountType == EightBitOneNumber) {
            auto last = mpCounter[n];
            if(last >= UINT8_MAX) {
                return UINT8_MAX;
            } else {
                auto latest = last+1;
                mpCounter[n] = latest;
                return latest;
            }            
        }
    }

    inline uint32_t get(uint32_t n) {
        if constexpr (bitCountType == FourBitOneNumber) {
            uint32_t base = n / 2;
            uint32_t remainder = n % 2;
            return (mpCounter[base] & (0xf0 >> (4*remainder))) >> ((1-remainder)*4);
        } else if constexpr (bitCountType == OneBitOneNumber) {
            auto byteIndex = n / 8;
            auto bitIndex = n % 8;
//            std::cout << "n " << n << " byteIndex " << byteIndex << " bitIndex " << bitIndex << "!\n";
            return (mpCounter[byteIndex] & (0x1 << (7-bitIndex))) >> (7-bitIndex);
        } else if constexpr (bitCountType == EightBitOneNumber) {
            return mpCounter[n];
        }
    }

    void test() {
        auto t = 318;

        // std::cout << setAndGet(t) << "!\n";
        // std::cout << get(t) << "!\n";
        // std::cout << setAndGet(t) << "!\n";
        // std::cout << get(t) << "!\n";
        // std::cout << setAndGet(t) << "!\n";  
        // std::cout << get(t) << "!\n";
        // std::cout << setAndGet(t) << "!\n";
        // std::cout << get(t) << "!\n";
        // std::cout << setAndGet(t) << "!\n";
        // std::cout << get(t) << "!\n";
        // std::cout << setAndGet(t) << "!\n";
        // std::cout << get(t) << "!\n";

        // for (size_t i = 0; i < 100; i++) {
        //     std::cout << get(i) << "!\n";
        // }

        for (size_t i = 0; i < 300; i++) {
            // std::cout << i << " status " << get(10) << "!\n";
            setAndGet(10);
            // std::cout << setAndGet(100) << "!\n";
            std::cout << i << " status " << get(10) << "!\n";
        }

        // for (size_t i = 0; i < 100; i++) {
        //     std::cout << get(i) << "!\n";
        // }
        
        
        // for (size_t i = 0; i < 17; i++)
        // {
        //     std::cout << setAndGet(1024) << "!\n";
        // }
        
        // std::cout << get(2999) << "!\n";

        // const short kDefaultMemoryFineness = sizeof(int);
        // constexpr uint32_t kMaxSize = 200*10000;
        // constexpr uint32_t kMaxMemorySize = (4*kMaxSize/8+kDefaultMemoryFineness*8-1) & ~(kDefaultMemoryFineness*8-1);
        // std::cout << kDefaultMemoryFineness << "!\n";
        // std::cout << ((kMaxMemorySize+4095) & ~4095) << "!\n";
    }

private:
    inline int add(int a, int b) {
        return b == 0 ? a : add(a ^ b, (a & b) << 1);
    }

private:
    uint32_t mMax = 0;
    uint8_t *mpCounter = nullptr;
    uint32_t kMaxMemorySize = bitCountType*kMaxSize/8;
};