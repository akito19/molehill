use std::env;
use std::fs::File;
use std::io::{self, Write};

fn generate_dig_file() -> Result<(), io::Error> {
    let content = include_str!("examples/notification.dig");
    let mut f = File::create("notification.dig").unwrap();
    write!(f, "{}", content).unwrap();
    f.flush().unwrap();
    Ok(())
}

fn generate_python_file() -> Result<(), io::Error> {
    let content = include_str!("examples/mailchimp.py");
    let mut f = File::create("mailchimp.py").unwrap();
    write!(f, "{}", content).unwrap();
    f.flush().unwrap();
    Ok(())
}

fn generate_sql_file() -> Result<(), io::Error> {
    let content = include_str!("examples/sample.sql");
    let mut f = File::create("sample.sql").unwrap();
    write!(f, "{}", content).unwrap();
    f.flush().unwrap();
    Ok(())
}

fn generate_html_file() -> Result<(), io::Error> {
    let content = include_str!("examples/template.html");
    let mut f = File::create("template.html").unwrap();
    write!(f, "{}", content).unwrap();
    f.flush().unwrap();
    Ok(())
}

#[allow(unused_must_use)]
fn generate_files() -> Result<(), String> {
    generate_dig_file();
    generate_python_file();
    generate_sql_file();
    generate_html_file();
    Ok(())
}

fn main() -> Result<(), io::Error> {
    let args: Vec<String> = env::args().collect();
    if args.len() > 1 {
        panic!("This tool expects no argument.")
    }

    match generate_files() {
        Ok(()) => {
            println!("Generated Digdag workflow files!");
        }
        Err(e) => {
            println!("Error: {}", e);
        }
    }
    Ok(())
}
