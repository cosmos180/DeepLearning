/*
 * @Author       : HouJinxin jinxinhou@tuputech.com
 * @Date         : 2024-11-29 02:54:16
 * @LastEditors  : HouJinxin jinxinhou@tuputech.com
 * @LastEditTime : 2025-04-02 03:15:50
 * @FilePath     : /DeepLearning/rust/src/main.rs
 * @Description  :
 *
 * Copyright (c) 2025 by @Me, All Rights Reserved.
 */
use reqwest::multipart;
use structopt::StructOpt;
use tokio::fs::File;

#[derive(StructOpt)]
#[structopt(name = "rurl", about = "A rust http client that mimics curl.")]
struct Opt {
    #[structopt(short, long)]
    upload: Option<String>,

    #[structopt(short, long)]
    download: Option<String>,

    #[structopt(short, long)]
    url: String,
}

async fn upload_file(url: &str, file_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let file = tokio::fs::read(file_path).await?;
    let part = multipart::Part::bytes(file).file_name(file_path.to_string());

    let form = multipart::Form::new().part("file", part);

    let client = reqwest::Client::new();
    let res = client.post(url).multipart(form).send().await?;

    println!("Response: {:?}", res.text().await?);
    Ok(())
}

async fn download_file(url: &str, file_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let res = client.get(url).send().await?;

    let mut file = File::create(file_path).await?;
    let content = res.bytes().await?;
    tokio::io::copy(&mut content.as_ref(), &mut file).await?;

    println!("File downloaded to {}", file_path);
    Ok(())
}

mod practise {
    pub mod r_box;
    pub mod r_list;
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // let opt = Opt::from_args();

    // if let Some(file_path) = opt.upload {
    //     upload_file(&opt.url, &file_path).await?;
    // } else if let Some(file_path) = opt.download {
    //     download_file(&opt.url, &file_path).await?;
    // }

    practise::r_box::run();
    practise::r_list::run();

    Ok(())
}
