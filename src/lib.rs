use std::io::Write;
use std::fs::File;

pub fn generate_default_files() -> Result<(), String> {
    generate_dig_file();
    generate_python_file();
    generate_sql_file();
    generate_html_file();
    Ok(())
}

fn generate_dig_file() {
    let content = include_str!("examples/notification.dig");
    let mut f = File::create("notification.dig").unwrap();
    write!(f, "{}", content).unwrap();
    f.flush().unwrap();
}

fn generate_python_file() {
    let content = include_str!("examples/mailchimp.py");
    let mut f = File::create("mailchimp.py").unwrap();
    write!(f, "{}", content).unwrap();
    f.flush().unwrap();
}

fn generate_sql_file() {
    let content = include_str!("examples/sample.sql");
    let mut f = File::create("sample.sql").unwrap();
    write!(f, "{}", content).unwrap();
    f.flush().unwrap();
}

fn generate_html_file() {
    let content = include_str!("examples/template.html");
    let mut f = File::create("template.html").unwrap();
    write!(f, "{}", content).unwrap();
    f.flush().unwrap();
}
