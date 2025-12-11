/*
 * @Author       : bughero bughero2012@gmail.com
 * @Date         : 2025-12-11 09:58:57
 * @LastEditors  : bughero bughero2012@gmail.com
 * @LastEditTime : 2025-12-11 10:00:41
 * @FilePath     : /DeepLearning/rust/frontend/src/main.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
use axum::Router;

#[tokio::main]
async fn main() {
    // 定义服务器监听地址
    let server_addr = "localhost:3000";

    // 创建路由器（目前为空，稍后添加路由）
    let router = Router::new();

    // 打印启动信息
    println!("启动前端服务: http://{server_addr}");

    // 绑定 TCP 监听器
    let listener = tokio::net::TcpListener::bind(&server_addr)
        .await
        .unwrap();

    // 启动 Axum 服务
    axum::serve(listener, router).await.unwrap();
}
