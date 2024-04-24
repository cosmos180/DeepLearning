/*
 * @Author: houjinxin
 * @Date: 2022-10-13 22:17:25
 * @Last Modified by: houjinxin
 * @Last Modified time: 2022-10-17 17:23:09
 */
#include "jason/BitmapCounter.h"
// #include "jason/CStringArray.h"
#include "jason/Cache.h"
#include "jason/STDMove.h"
#include "jason/STLType.h"
#include "jason/SharePTR.h"
#include "jason/air/air_pthread_reader_writer.h"
#include "jason/air/air_thread_safe_queue.h"
#include "jason/air/air_unordered_map.h"
#include "jason/molest_cpp_11/cpp_molest.h"
#include "jason/network.h"

#include "jason.h"

template <typename Target>
int runTargetMethod() {
    Target *t = new Target();
    t->test();
    delete t;
    t = nullptr;
    return 0;
}

// DECLARATION(timestamp, tag, now); \

#define RUN(T) runTargetMethod<T>()
#define CONTACT_STR(tag) #tag.c_str()
#define DECLARATION_VALUE(name, tag, now) static auto name##_tag = now;
#define FPSBenchmarkDefine(tag)                                                                    \
    do {                                                                                           \
        auto now = std::chrono::duration_cast<std::chrono::milliseconds>(                          \
                       std::chrono::system_clock::now().time_since_epoch())                        \
                       .count();                                                                   \
        static uint64_t frameIndex = 0;                                                            \
        printf("----cid %s fps %f\n", tag.c_str(),                                                 \
               1000.0f * (++frameIndex) / (now - mFirstFrameTimestamp));                           \
    } while (0);

#define FPSBenchmarkDeclareation uint64_t mFirstFrameTimestamp = 0
#define CONCAT(a, b) CONCAT_INNER(a, b)
#define CONCAT_INNER(a, b) a##b
#define UNIQUE_NAME(base) CONCAT(base, __COUNTER__)

int main() {
    // RUN(SharePTR);
    // RUN(AIR_THREAD_SAFE_QUEUE);
    // RUN(UnorderedMap);
    RUN(AIR_PTHREAD_READER_WRITER);

    // JASON::Linux::epollTest();

    CPPMolest::molest_type_index();

    return 0;
}