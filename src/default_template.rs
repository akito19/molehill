use std::io::{Write, Error};
use std::fs::File;

pub fn generate_files(output: &str) -> Result<(), Error> {
    generate_dig_file(output);
    generate_python_file(output);
    generate_sql_file(output);
    generate_html_file(output);
    Ok(())
}

fn generate_dig_file(output: &str) {
    let content = include_str!("examples/notification.dig");
    let path = output.to_string() + "/notification.dig";
    let mut file = File::create(path).unwrap();
    write!(file, "{}", content).unwrap();
    file.flush().unwrap();
}

fn generate_python_file(output: &str) {
    let content = include_str!("examples/mailchimp.py");
    let path = output.to_string() + "/mailchimp.py";
    let mut file = File::create(path).unwrap();
    write!(file, "{}", content).unwrap();
    file.flush().unwrap();
}

fn generate_sql_file(output: &str) {
    let content = include_str!("examples/sample.sql");
    let path = output.to_string() + "/sample.sql";
    let mut file = File::create(path).unwrap();
    write!(file, "{}", content).unwrap();
    file.flush().unwrap();
}

fn generate_html_file(output: &str) {
    let content = include_str!("examples/template.html");
    let path = output.to_string() + "/template.html";
    let mut file = File::create(path).unwrap();
    write!(file, "{}", content).unwrap();
    file.flush().unwrap();
}
