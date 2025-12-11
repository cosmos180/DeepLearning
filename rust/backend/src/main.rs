/*
 * @Author       : bughero bughero2012@gmail.com
 * @Date         : 2025-12-11 09:59:18
 * @LastEditors  : bughero bughero2012@gmail.com
 * @LastEditTime : 2025-12-11 10:01:35
 * @FilePath     : /DeepLearning/rust/backend/src/main.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
use axum::Router;

#[tokio::main]
async fn main() {
    // 后端使用 3100 端口，与前端区分
    let server_addr = "localhost:3100";

    // 创建空路由器
    let router = Router::new();

    // 打印启动信息
    println!("启动后端服务: http://{server_addr}");

    // 绑定监听器并启动服务
    let listener = tokio::net::TcpListener::bind(&server_addr)
        .await
        .unwrap();
    axum::serve(listener, router).await.unwrap();
}
