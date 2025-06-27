/*
 * @Author       : bughero bughero2012@gmail.com
 * @Date         : 2025-06-06 17:32:22
 * @LastEditors  : bughero bughero2012@gmail.com
 * @LastEditTime : 2025-06-06 18:05:14
 * @FilePath     : /DeepLearning/rust/build.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
fn main() {
    cxx_build::bridge("src/main.rs")
        .file("cpp/src/blobstore.cc")
        .compile("cxx-demo");

    println!("cargo:rerun-if-changed=src/main.rs");
    println!("cargo:rerun-if-changed=src/cpp/src/blobstore.cc");
    println!("cargo:rerun-if-changed=src/cpp/include/blobstore.h");
}
