#[cfg(test)]
mod tests {
    use super::*;
    use cxx::let_cxx_string;
    use std::env;
    use std::fs;
    use std::path::Path;

    // 测试 analyze_image_sync (路径)
    #[test]
    fn test_analyze_image_sync() {
        let_cxx_string!(
            api_key = match env::var("OPENAI_API_KEY") {
                Ok(val) => val,
                Err(_) => return, // 跳过测试
            }
        );
        let_cxx_string!(image_path = "/home/bughero/Desktop/car_4s_store.jpg");
        let image_path_str = image_path.to_str().unwrap();
        if !Path::new(image_path_str).exists() {
            eprintln!("测试图片不存在，跳过 test_analyze_image_sync");
            return;
        }
        let result = analyze_image_sync(&image_path, &api_key);

        print!("Result: {}", result);
        assert!(result.contains("Status: "));
        assert!(result.contains("Response: "));
    }

    // 测试 analyze_image_buffer_sync (buffer)
    #[test]
    fn test_analyze_image_buffer_sync() {
        let_cxx_string!(
            api_key = match env::var("OPENAI_API_KEY") {
                Ok(val) => val,
                Err(_) => return, // 跳过测试
            }
        );
        let image_path = "/home/bughero/Desktop/car_4s_store.jpg";
        if !Path::new(image_path).exists() {
            eprintln!("测试图片不存在，跳过 test_analyze_image_buffer_sync");
            return;
        }
        let jpeg_buf = fs::read(image_path).unwrap();
        let result = analyze_image_buffer_sync(&jpeg_buf, &api_key);
        print!("Result: {}", result);

        assert!(result.contains("Status: "));
        assert!(result.contains("Response: "));
    }
}
use base64::{engine::general_purpose, Engine as _};
use cxx::CxxString;
use once_cell::sync::OnceCell;
use reqwest::header::{AUTHORIZATION, CONTENT_TYPE};
use serde_json::json;
use std::error::Error;
use std::{env, fs};
use tokio::runtime::Runtime;

// 异步分析图片路径
async fn analyze_image(image_path: &str, api_key: &str) -> Result<String, Box<dyn Error>> {
    let image_bytes = fs::read(image_path)?;
    analyze_image_buffer(&image_bytes, api_key).await
}

// 异步分析 jpeg buffer
async fn analyze_image_buffer(jpeg_buf: &[u8], api_key: &str) -> Result<String, Box<dyn Error>> {
    let base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions";
    let base64_image = general_purpose::STANDARD.encode(jpeg_buf);
    let user_content = vec![
        json!({
            "type": "image_url",
            "image_url": { "url": format!("data:image/jpeg;base64,{}", base64_image) }
        }),
        json!({
            "type": "text",
            "text": "图片中有没有出现【顾客手持手机、手机支付二维码、现金】。如果有，请用 json {'customer_holding_mobile_phone': bool, 'mobile_payment_QR_code':bool, 'cash': bool} 格式返回，只需要返回json结果即可，不需要分析过程、解释、说明。"
        }),
    ];
    let req_body = json!({
        "model": "qwen-vl-plus-latest",
        "messages": [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}]
            },
            {
                "role": "user",
                "content": user_content
            }
        ]
    });
    let client = reqwest::Client::new();
    let resp = client
        .post(base_url)
        .header(AUTHORIZATION, format!("Bearer {}", api_key))
        .header(CONTENT_TYPE, "application/json")
        .json(&req_body)
        .send()
        .await?;
    let status = resp.status();
    let text = resp.text().await?;
    Ok(format!("Status: {}\nResponse: {}", status, text))
}

// cxx::bridge FFI
#[cxx::bridge]
mod ffi {
    extern "Rust" {
        fn analyze_image_sync(image_path: &CxxString, api_key: &CxxString) -> String;
        fn analyze_image_buffer_sync(jpeg_buf: &[u8], api_key: &CxxString) -> String;
    }
}
// 提供同步接口给 C++ 调用（buffer 版本）
pub fn analyze_image_buffer_sync(jpeg_buf: &[u8], api_key: &CxxString) -> String {
    static RUNTIME: OnceCell<Runtime> = OnceCell::new();
    let rt = RUNTIME.get_or_init(|| Runtime::new().unwrap());
    match rt.block_on(analyze_image_buffer(jpeg_buf, api_key.to_str().unwrap())) {
        Ok(res) => res,
        Err(e) => format!("Error: {}", e),
    }
}

// 提供同步接口给 C++ 调用
pub fn analyze_image_sync(image_path: &CxxString, api_key: &CxxString) -> String {
    static RUNTIME: OnceCell<Runtime> = OnceCell::new();
    let rt = RUNTIME.get_or_init(|| Runtime::new().unwrap());
    match rt.block_on(analyze_image(
        image_path.to_str().unwrap(),
        api_key.to_str().unwrap(),
    )) {
        Ok(res) => res,
        Err(e) => format!("Error: {}", e),
    }
}

// 可选: 保留 main 便于本地测试
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let api_key = env::var("OPENAI_API_KEY").expect("请先设置 OPENAI_API_KEY 环境变量");
    let image_path = "/home/bughero/Desktop/car_4s_store.jpg";
    let result = analyze_image(image_path, &api_key).await?;
    println!("{}", result);
    Ok(())
}
