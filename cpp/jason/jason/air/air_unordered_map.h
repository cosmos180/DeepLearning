/*
 * @Author: your name
 * @Date: 2020-11-25 19:02:09
 * @LastEditTime: 2023-09-13 10:55:25
 * @LastEditors: bughero jinxinhou@tuputech.com
 * @Description: In User Settings Edit
 * @FilePath: /DeepLearning/cpp/jason/jason/air/air_unordered_map.h
 */
#include <array>
#include <mutex>
#include <stdio.h>
#include <unordered_map>

#include "air_base.h"

class UnorderedMap : public AIR_BASE {
  private:
    std::mutex gMutex;
    std::unordered_map<std::string, size_t> gCIDList;

  protected:
    void doTest() {
        //   std::unordered_map<std::string, int *> test;
        //   printf("9 index value %p\n", test["123"]);

        //   uint32_t inout[16];
        //   memset_s(inout, sizeof(inout), 0, sizeof(inout));
        //   for (int i = 0, n = sizeof(inout); i < n; i++) {
        //       printf("i %d value %u\n", i, inout[i]);
        //   }

        printf("__constrain_hash(36316511, %u) == %zu\n", 2, __constrain_hash(36316512, 2));

        for (size_t i = 1; i < 129; i++) {
            // printf("__constrain_hash(36316511, %zu) == %zu\n", i, __constrain_hash(36316512, i));
            // // printf("__constrain_hash(36316512, %zu) == %zu\n", i, __constrain_hash(i,
            // 36316512));
            // // printf("__constrain_hash(36316513, %zu) == %zu\n", i, __constrain_hash(i,
            // 36316513));
            printf("%zu __is_hash_power2: %d\n", i, __is_hash_power2(i));
        }
    }

    size_t __constrain_hash(size_t __h, size_t __bc) {
        return !(__bc & (__bc - 1)) ? __h & (__bc - 1) : (__h < __bc ? __h : __h % __bc);
    }

    bool __is_hash_power2(size_t __bc) { return __bc > 2 && !(__bc & (__bc - 1)); }

    size_t transformCID2ChannelId(const std::string &&cid) {
        std::lock_guard<std::mutex> lk(gMutex);

        auto channelId = -1;
        auto result = gCIDList.find(cid);
        if (result != gCIDList.end()) {
            channelId = result->second;
        } else {
            channelId = gCIDList.size() + 1;
            gCIDList.emplace(cid, channelId);
        }

        return channelId;
    }
};
