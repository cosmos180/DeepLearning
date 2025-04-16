/*
 * @Author       : HouJinxin jinxinhou@tuputech.com
 * @Date         : 2025-04-16 09:07:17
 * @LastEditors  : HouJinxin jinxinhou@tuputech.com
 * @LastEditTime : 2025-04-16 10:30:06
 * @FilePath     : /DeepLearning/rust/src/practise/r_result.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
use std::fs::File;
use std::io::ErrorKind;
use std::io::{self, Read};
use std::net::IpAddr;

fn read_username_from_file() -> Result<String, io::Error> {
    let mut username = String::new();

    File::open("hello.txt")?.read_to_string(&mut username)?;

    Ok(username)
}

pub fn run() {
    let user_name = read_username_from_file();
    match user_name {
        Ok(name) => println!("Username: {name}"),
        Err(e) => match e.kind() {
            ErrorKind::NotFound => println!("File not found"),
            ErrorKind::PermissionDenied => println!("Permission denied"),
            _ => println!("An error occurred: {}", e),
        },
    }

    let home: IpAddr = "127.0.0.1"
        .parse()
        .expect("Hardcoded IP address should be valid");
    print!("home: {}", home)
}
