//
//  OSLockPerformanceTest.m
//  test
//
//  Created by 候 金鑫 on 16/8/24.
//  Copyright © 2016年 候 金鑫. All rights reserved.
//

#import "OSLockPerformanceTest.h"
#import <objc/runtime.h>
#import <objc/message.h>
#import <libkern/OSAtomic.h>
#import <pthread.h>

@implementation OSLockPerformanceTest
#define ITERATIONS (10000000) // 1千万
+ (void)test
{
    double then, now;
    
    @autoreleasepool {
        
        // NSLock
        NSLock *lock = [NSLock new];
        then = CFAbsoluteTimeGetCurrent();
        for(NSInteger i = 0; i < ITERATIONS; ++i)
        {
            [lock lock];
            [lock unlock];
        }
        now = CFAbsoluteTimeGetCurrent();
        printf("NSLock: %f sec\n", now-then);
        
        // pthread_mutex
        pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
        then = CFAbsoluteTimeGetCurrent();
        for(NSInteger i = 0; i < ITERATIONS; ++i)
        {
            pthread_mutex_lock(&mutex);
            pthread_mutex_unlock(&mutex);
        }
        now = CFAbsoluteTimeGetCurrent();
        printf("pthread_mutex: %f sec\n", now-then);
        
        // OSSpinlock
        OSSpinLock spinlock = OS_SPINLOCK_INIT;
        then = CFAbsoluteTimeGetCurrent();
        for(NSInteger i = 0; i < ITERATIONS; ++i)
        {
            OSSpinLockLock(&spinlock);
            OSSpinLockUnlock(&spinlock);
        }
        now = CFAbsoluteTimeGetCurrent();
        printf("OSSpinlock: %f sec\n", now-then);
        
        // synchronized
        id obj = [NSObject new];
        then = CFAbsoluteTimeGetCurrent();
        for(NSInteger i = 0; i < ITERATIONS; ++i)
        {
            @synchronized(obj)
            {
            }
        }
        now = CFAbsoluteTimeGetCurrent();
        printf("@synchronized: %f sec\n", now-then);
        
        // dispatch_barrier_async
        dispatch_queue_t queue = dispatch_queue_create("com.sharemerge.lock", DISPATCH_QUEUE_CONCURRENT);
        for(NSInteger i = 0; i < ITERATIONS; ++i)
        {
            dispatch_barrier_async(queue, ^{
            });
        }
        now = CFAbsoluteTimeGetCurrent();
        printf("dispatch_barrier_async: %f sec\n", now-then);
        
        // dispatch_semaphore
        dispatch_semaphore_t lockSemaphore = dispatch_semaphore_create(1);
        for(NSInteger i = 0; i < ITERATIONS; ++i)
        {
            dispatch_semaphore_wait(lockSemaphore, DISPATCH_TIME_FOREVER);
            dispatch_semaphore_signal(lockSemaphore);
        }
        now = CFAbsoluteTimeGetCurrent();
        printf("dispatch_semaphore: %f sec\n", now-then);
    }
}
@end
