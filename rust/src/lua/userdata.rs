/*
 * @Author       : bughero bughero2012@gmail.com
 * @Date         : 2025-05-28 14:41:38
 * @LastEditors  : bughero bughero2012@gmail.com
 * @LastEditTime : 2025-06-04 18:07:44
 * @FilePath     : /DeepLearning/rust/src/lua/userdata.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
use mlua::{chunk, Lua, MetaMethod, Result, UserData};

#[derive(Default)]
struct Rectangle {
    length: u32,
    width: u32,
}

impl UserData for Rectangle {
    fn add_fields<F: mlua::UserDataFields<Self>>(fields: &mut F) {
        fields.add_field_method_get("length", |_, this| Ok(this.length));
        fields.add_field_method_set("length", |_, this, val| {
            this.length = val;
            Ok(())
        });
        fields.add_field_method_get("width", |_, this| Ok(this.width));
        fields.add_field_method_set("width", |_, this, val| {
            this.width = val;
            Ok(())
        });
    }

    fn add_methods<M: mlua::UserDataMethods<Self>>(methods: &mut M) {
        methods.add_method("area", |_, this, ()| Ok(this.length * this.width));
        methods.add_method("diagonal", |_, this, ()| {
            Ok((this.length.pow(2) as f64 + this.width.pow(2) as f64).sqrt())
        });

        // Constructor
        methods.add_meta_function(MetaMethod::Call, |_, ()| Ok(Rectangle::default()));
    }
}

pub fn run() -> Result<()> {
    let lua = Lua::new();
    let rectangle = Rectangle::default();

    let ret = lua
        .load(chunk! {
            local rect = $rectangle()
            rect.width = 10
            rect.length = 5
            assert(rect:area() == 50)
            assert(rect:diagonal() - 11.1803 < 0.0001)
        })
        .exec();

    match ret {
        Ok(()) => println!("Lua script executed successfully!"),
        Err(e) => println!("An error occurred: {}", e),
    }

    Ok(())
}
