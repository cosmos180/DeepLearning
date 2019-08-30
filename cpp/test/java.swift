//
//  java.swift
//  test
//
//  Created by bug小英雄 on 2017/3/31.
//  Copyright © 2017年 候 金鑫. All rights reserved.
//

import Cocoa

class java: NSObject {
    class func xixi() {
        let total = 1000000000
        var i = 0
        var sum = 0
        while i <= total {
            sum = sum + i
            i += 1
        }
        print(sum)
    }
}
