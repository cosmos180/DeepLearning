/*
 * @Author       : HouJinxin jinxinhou@tuputech.com
 * @Date         : 2025-04-02 03:10:10
 * @LastEditors  : HouJinxin jinxinhou@tuputech.com
 * @LastEditTime : 2025-04-02 03:18:11
 * @FilePath     : /DeepLearning/rust/src/practise/r_list.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
#[derive(Debug)]
enum List {
    Cons(i32, Box<List>),
    Nil,
}

impl List {
    pub fn print(&self) {
        match self {
            List::Cons(value, next) => {
                print!("{} -> ", value);
                next.print();
            }
            List::Nil => {
                println!("Nil");
            }
        }
    }
}

pub fn run() {
    let list = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));
    list.print();
}
