//
//  main.m
//  test
//
//  Created by 候 金鑫 on 16/4/6.
//  Copyright © 2016年 候 金鑫. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "OSLockPerformanceTest.h"

#define TICK  NSDate *startTime = [NSDate date]
#define TOCK  NSLog(@"Time:%f",-[startTime timeIntervalSinceNow])

extern int start_mysection __asm("section$start$__DATA$__mysection");
extern int stop_mysection  __asm("section$end$__DATA$__mysection");

static int x __attribute__((used,section("__DATA,__mysection"))) = 4;
static int y __attribute__((used,section("__DATA,__mysection"))) = 10;
static int z __attribute__((used,section("__DATA,__mysection"))) = 22;


//#define Rank(NO) (@"icon_rank_"#NO)
#define RankImage(NO) [NSString stringWithFormat:@"icon_rank_%d", NO]

int main(int argc, const char * argv[]) {
    @autoreleasepool {
////        int a[5] = {1,2,3,4,5};
////        int *ptr = (int*)(&a+1);
////        printf("%d, %d", *(a+1), *(ptr-1));
////        
////        for (int i=1; i<51; i++) {
////            NSLog(@"%@", RankImage(i));
////        }
//        
//        int i = 0;
////        int nDevCount = sizeof(kSzDevUid);
//        for (i = 0; i < 10; i++) {
//            
//        }
////        return i < nDevCount;
//        NSLog(@"%d", i);
//        
//        
//        NSArray *szNull = NULL;
////        NSObject *object = [szNull objectAtIndex:0];
//        NSObject *object = szNull[0];
//        [szNull indexOfObjectIdenticalTo:object];
//        NSLog(@"%@", object);
//        
//        TICK;
//        NSArray *numbers = @[@9, @5, @11, @3, @1];
//        NSArray *sortedNumbers = [numbers sortedArrayUsingSelector:@selector(compare:)];
//        NSLog(@"%@", sortedNumbers);
//        TOCK;
//        
////        TICK;
//        NSArray *array = @[@"John Appleseed", @"Tim Cook", @"Hair Force One", @"Michael Jurewitz"];
//        NSArray *sortedArray = [array sortedArrayUsingSelector:@selector(localizedCaseInsensitiveCompare:)];
//        NSLog(@"%@", sortedArray);
////        TOCK;
//        [OSLockPerformanceTest test];
        
//        NSLog(@"1"); //任务1
//        dispatch_sync(dispatch_get_main_queue(), ^{
//            NSLog(@"2"); //任务2
//        });
//        NSLog(@"3"); //任务3
        
//        dispatch_queue_t queue = dispatch_queue_create("myQueue", DISPATCH_QUEUE_SERIAL);
//        NSLog(@"1"); //任务1
//        dispatch_async(queue, ^{
//                NSLog(@"2"); //任务2
//                dispatch_sync(queue, ^{
//                    NSLog(@"3"); //任务3
//                });
//                NSLog(@"4"); //任务4
//            });
//            NSLog(@"5"); //任务5
//        }
    
//        //循环执行任务，任务的顺序是无序列的并且会堵塞当前的线程。
        dispatch_queue_t queue = dispatch_queue_create("myQueue", DISPATCH_QUEUE_SERIAL);
//        // count: 循环执行次数
//        // queue: 队列，可以是串行队列或者是并行队列
//        // block: 任务
//        dispatch_apply(5, queue, ^(size_t i) {
//            NSLog(@"%zu %@", i, [NSThread currentThread]);
//        });
        
        dispatch_async(queue, ^{ printf("1"); });
        printf("2");
        dispatch_async(queue, ^{ printf("3"); });
        printf("4");
        
        long sz = &stop_mysection - &start_mysection;
        long i;
        
        printf("Section size is %ld\n", sz);
        
        for (i=0; i < sz; ++i) {
            printf("%d\n", (&start_mysection)[i]);
        }
        
        char *opCode = '\x81';
        printf("Section size is %d\n", (unsigned int)opCode);
        
//        header.fin = !!(SRFinMask & headerBuffer[0]);
        BOOL fin = !!(0x80 & 0x81);
        printf("Section size is %d\n", (int)fin);
        
        
        NSNumberFormatter *formatter = [[NSNumberFormatter alloc] init];
        [formatter setAlwaysShowsDecimalSeparator:NO];
        [formatter setAllowsFloats:YES];
        [formatter setFormatterBehavior:NSNumberFormatterBehavior10_4];
        [formatter setMinimumFractionDigits:2];
        [formatter setMaximumFractionDigits:2];
//        [formatter setNumberStyle:kCFNumberFormatterDecimalStyle];
        formatter.numberStyle = NSNumberFormatterDecimalStyle;
        NSNumber *number = [NSNumber numberWithFloat:65];
        NSLog(@"%@", [formatter stringFromNumber:number]);
        
        /*
         #pragma mark -
         #pragma mark ------------  ios开发之倒计时实现的两种方法 ------------
         */
        while (1) {
            __block int timeout=300; //倒计时时间
            dispatch_queue_t timerQueue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
            dispatch_source_t _timer = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, timerQueue);
            dispatch_source_set_timer(_timer, dispatch_walltime(NULL, 0), 1.0*NSEC_PER_SEC, 0); //每秒执行
            dispatch_source_set_event_handler(_timer, ^{
                if(timeout<=0){ //倒计时结束，关闭
                    dispatch_source_cancel(_timer);
                    dispatch_async(dispatch_get_main_queue(), ^{
                        NSLog(@"倒计时结束，关闭, currentThread = %@", [NSThread currentThread]);
                    });
                }else{
                    int minutes = timeout / 60;
                    int seconds = timeout % 60;
                    NSString *strTime = [NSString stringWithFormat:@"%d分%.2d秒后重新获取验证码", minutes, seconds];
                    dispatch_async(dispatch_get_main_queue(), ^{
                        NSLog(@"%@------%@", strTime, [NSThread currentThread]);
                    });
                    timeout--;
                    
                }  
            });  
            dispatch_resume(_timer);
        }

    }
    return 0;
}
