/*
 * @Author       : bughero bughero2012@gmail.com
 * @Date         : 2025-06-05 15:32:47
 * @LastEditors  : bughero bughero2012@gmail.com
 * @LastEditTime : 2025-06-09 19:12:07
 * @FilePath     : /DeepLearning/rust/src/lua/lua_engine.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
use mlua::{Lua, Result as LuaResult, Value, MultiValue};
use std::fs;
use std::path::Path;

/// 读取指定路径的 Lua 文件并执行，输出结果或错误。
pub fn run_lua_file<P: AsRef<Path>>(path: P) {
    // 1. 读取文件内容
    let code = match fs::read_to_string(&path) {
        Ok(s) => s,
        Err(e) => {
            eprintln!(
                "[Error] Failed to read lua file {}: {}",
                path.as_ref().display(),
                e
            );
            return;
        }
    };

    // print!("[Lua Code] {}\n", code);

    // 2. 创建 Lua 虚拟机
    let lua = Lua::new();

    // 3. 执行 Lua 代码
    match lua.load(&code).eval::<Value>() {
        Ok(result) => {
            println!("[Lua]: {:?}", result);
        }
        Err(e) => {
            eprintln!("[Error] Lua execution failed: {}", e);
        }
    }
}

// 示例用法（可在 main.rs 或测试中调用）
// run_lua_file("lua/hello.lua");

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    use std::path::PathBuf;

    // #[test]
    fn test_run_lua_file_success() {
        // 创建临时 Lua 文件
        let mut path = PathBuf::from("/tmp/test_hello.lua");
        let code = r#"return 42"#;
        {
            let mut file = File::create(&path).expect("Failed to create temp lua file");
            file.write_all(code.as_bytes())
                .expect("Failed to write lua code");
        }
        // 执行 Lua 文件
        run_lua_file(&path);
        // 清理
        let _ = std::fs::remove_file(&path);
    }

    #[test]
    fn test_run_input_lua_file() {
        // 创建临时 Lua 文件
        let mut path =
            PathBuf::from("/home/bughero/Documents/github/DeepLearning/rust/src/lua/input.lua");

        // 执行 Lua 文件
        run_lua_file(&path);
    }

    // #[test]
    fn test_run_lua_file_not_found() {
        // 文件不存在
        let path = "/tmp/non_existent.lua";
        run_lua_file(path);
    }
}

/// 动态加载 Lua 文件并调用指定函数，传递参数
pub fn call_lua_function<P: AsRef<Path>>(
    lua_file: P,
    func_name: &str,
    args: &[Value],
) -> mlua::Result<Vec<f64>> {
    // 读取 Lua 文件
    let code = fs::read_to_string(&lua_file)
        .map_err(|e| mlua::Error::external(format!("Read lua file error: {}", e)))?;
    
    let lua = Lua::new();
    // 加载脚本
    lua.load(&code).exec()?;
    // 获取函数并调用
    let globals = lua.globals();
    let func: mlua::Function = globals.get(func_name)?;
    let result = func.call(MultiValue::from_vec(args.to_vec()))?;

    // 根据返回值类型进行转换
    match result {
        Value::Table(tbl) => {
            let len = tbl.clone().pairs::<Value, Value>().count();
            let mut vals = Vec::with_capacity(len);
            
            // Convert sequential table elements to Vec<f64>
            for i in 1..=len as i64 {
                match tbl.get(Value::Integer(i))? {
                    Value::Number(n) => vals.push(n),
                    Value::Integer(i) => vals.push(i as f64),
                    v => return Err(mlua::Error::external(format!(
                        "Unexpected value type in table at index {}: {:?}", 
                        i, v
                    ))),
                }
            }
            Ok(vals)
        },
        Value::Number(n) => Ok(vec![n]),
        Value::Integer(i) => Ok(vec![i as f64]),
        Value::Nil => Ok(vec![]),
        v => Err(mlua::Error::external(format!(
            "Unexpected return type: {:?}", 
            v
        ))),
    }
}

#[cfg(test)]
mod dynamic_call_tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_call_lua_function_crop_rect() {
        let lua_path = PathBuf::from("./src/lua/input.lua");
        // 参数: raw_frame_width, raw_frame_height, left, top, right, bottom
        let args = [
            Value::Integer(1920),
            Value::Integer(1080),
            Value::Number(100.0),
            Value::Number(150.0),
            Value::Number(600.0),
            Value::Number(800.0),
        ];
        
        let result = call_lua_function(&lua_path, "calculate_crop_QRCode_rect", &args)
            .expect("Function call failed");
        
        println!("Crop rect result: {:?}", result);
        assert_eq!(result.len(), 4);
        // 验证返回值是否在合理范围内
        assert!(result[0] >= 0.0 && result[0] <= 1920.0); // x
        assert!(result[1] >= 0.0 && result[1] <= 1080.0); // y
        assert!(result[2] > 0.0 && result[2] <= 1920.0);  // width
        assert!(result[3] > 0.0 && result[3] <= 1080.0);  // height
    }

    #[test]
    fn test_call_lua_function_fact() {
        let lua_path = PathBuf::from("./src/lua/input.lua");
        let args = [Value::Integer(5)];
        
        let result = call_lua_function(&lua_path, "fact", &args)
            .expect("Function call failed");
            
        println!("Factorial of 5: {}", result[0]);
        assert_eq!(result[0], 120.0); // 5! = 120
    }

    #[test]
    fn test_call_lua_function_not_found() {
        let lua_path = PathBuf::from("./src/lua/input.lua");
        let args = [];
        let result = call_lua_function(&lua_path, "not_exist_func", &args);
        assert!(result.is_err());
    }
}
