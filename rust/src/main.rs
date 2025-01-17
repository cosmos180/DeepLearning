use reqwest::multipart;
use structopt::StructOpt;
use tokio::fs::File;
use tokio::io::AsyncReadExt;

#[derive(StructOpt)]
#[structopt(name = "rcurl", about = "A simple HTTP client.")]
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
    let mut content = res.bytes().await?;
    tokio::io::copy(&mut content.as_ref(), &mut file).await?;

    println!("File downloaded to {}", file_path);
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let opt = Opt::from_args();

    if let Some(file_path) = opt.upload {
        upload_file(&opt.url, &file_path).await?;
    } else if let Some(file_path) = opt.download {
        download_file(&opt.url, &file_path).await?;
    }

    Ok(())
}
