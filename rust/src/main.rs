/*
 * @Author       : HouJinxin jinxinhou@tuputech.com
 * @Date         : 2024-11-29 02:12:50
 * @LastEditors  : HouJinxin jinxinhou@tuputech.com
 * @LastEditTime : 2024-11-29 02:46:26
 * @FilePath     : /DeepLearning/rust/src/main.rs
 * @Description  :
 *
 * Copyright (c) 2024 by @Me, All Rights Reserved.
 */

// use rusqlite::{Connection, Result};

// #[derive(Debug)]
// struct Person {
//     id: i32,
//     name: String,
//     data: Option<Vec<u8>>,
// }

// fn main() -> Result<()> {
//     let conn = Connection::open_in_memory()?;

//     conn.execute(
//         "CREATE TABLE person (
//             id    INTEGER PRIMARY KEY,
//             name  TEXT NOT NULL,
//             data  BLOB
//         )",
//         (), // empty list of parameters.
//     )?;
//     let me = Person {
//         id: 0,
//         name: "Steven".to_string(),
//         data: None,
//     };
//     conn.execute(
//         "INSERT INTO person (name, data) VALUES (?1, ?2)",
//         (&me.name, &me.data),
//     )?;

//     let mut stmt = conn.prepare("SELECT id, name, data FROM person")?;
//     let person_iter = stmt.query_map([], |row| {
//         Ok(Person {
//             id: row.get(0)?,
//             name: row.get(1)?,
//             data: row.get(2)?,
//         })
//     })?;

//     for person in person_iter {
//         println!("Found person {:?}", person.unwrap());
//     }

//     Ok(())
// }

// use reqwest::Error;

// #[tokio::main]
// async fn main() -> Result<(), Error> {
//     let response = reqwest::get("http://httpbin.org/get").await?;
//     let body = response.text().await?;
//     println!("body = {:?}", body);
//     Ok(())
// }

use std::io;

fn println_test() {
    let x = 5;
    let y = 10;

    println!("x = {x} and y + 2 = {}", y + 2);
}

fn main() {
    println!("Guess the number!");
    println!("Please input your guess.");

    let mut guess = String::new();

    io::stdin()
        .read_line(&mut guess)
        .expect("Failed to read line");

    println!("You guessed: {}", guess);

    println_test();
}
