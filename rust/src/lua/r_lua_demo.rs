/*
 * @Author       : bughero bughero2012@gmail.com
 * @Date         : 2025-05-28 12:38:33
 * @LastEditors  : bughero bughero2012@gmail.com
 * @LastEditTime : 2025-05-28 14:26:19
 * @FilePath     : /DeepLearning/rust/src/lua/r_lua_demo.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
use mlua::prelude::*;

fn test() -> LuaResult<()> {
    let lua = Lua::new();

    let map_table = lua.create_table()?;
    map_table.set(1, "one")?;
    map_table.set("two", 2)?;

    lua.globals().set("map_table", map_table)?;

    lua.load("for k,v in pairs(map_table) do print(k,v) end")
        .exec()?;

    Ok(())
}

pub fn run() {
    let _ = test();
}
