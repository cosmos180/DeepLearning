/*
 * @Author       : HouJinxin jinxinhou@tuputech.com
 * @Date         : 2025-04-16 08:54:50
 * @LastEditors  : HouJinxin jinxinhou@tuputech.com
 * @LastEditTime : 2025-04-16 08:56:55
 * @FilePath     : /DeepLearning/rust/src/practise/r_panic.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
pub fn run() {
    // panic!("crash and burn");

    let v = vec![1, 2, 3];

    v[99];
}
