//
//  multithread_memory_model.hpp
//  test
//
//  Created by bug小英雄 on 2018/1/4.
//  Copyright © 2018年 候 金鑫. All rights reserved.
//

#ifndef multithread_memory_model_hpp
#define multithread_memory_model_hpp

namespace Dabiq {
    struct CPlusPlusMultiThreadMemoryModel {
        /************relaxed_memory*************/
//        static void relaxed_memory_producer();
//        static void relaxed_memory_consumer();
        /***********End************************/
        
        /************relaxed_memory*************/
        static void memory_order_release_producer();
        static void memory_order_acquire_consumer();
        /***********End************************/
        
        /************relaxed_memory*************/
        static void memory_order_consume_consumer();
        /***********End************************/

        
        static void print_result();
    };

}

#endif /* multithread_memory_model_hpp */
