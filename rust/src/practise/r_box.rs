/*
 * @Author       : HouJinxin jinxinhou@tuputech.com
 * @Date         : 2025-04-02 03:01:15
 * @LastEditors  : HouJinxin jinxinhou@tuputech.com
 * @LastEditTime : 2025-04-02 03:04:58
 * @FilePath     : /DeepLearning/rust/src/practise/box.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
pub fn run() {
    let b = Box::new(5);
    println!("b = {}", b);
}
