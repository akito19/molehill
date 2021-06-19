use std::path::Path;
use std::process;
// Modules
use molehill::default_template;
use molehill::template;

// External crates
extern crate exitcode;
use clap::{App, Arg};

fn main() {
    let matches = App::new("MoleHill")
        .version("0.2.1")
        .about("Generate Workflow template files.")
        .arg(
            Arg::new("template")
                .short('t')
                .long("template")
                .value_name("PATH")
                .about("Set Digdag workflow template directory.")
                .takes_value(true),
        )
        .arg(
            Arg::new("output")
                .short('o')
                .long("output")
                .value_name("PATH")
                .default_value(".")
                .about("Output file path. The current directory is to default.")
                .takes_value(true),
        )
        .get_matches();

    let output = matches.value_of("output").unwrap();

    if !(Path::new(output.clone()).is_dir()) {
        eprintln!("Specify directory path for `-o` / `--output` option.");
        process::exit(exitcode::USAGE);
    }

    if let Some(template) = matches.value_of("template") {
        if !(Path::new(template.clone()).is_dir()) {
            eprintln!("Specify directory path for `-t` / `--template` option.");
            process::exit(exitcode::USAGE);
        }
        match template::generate_files(template, output) {
            Ok(()) => {
                println!("Generated Digdag workflow files!");
                process::exit(exitcode::OK);
            }
            Err(e) => {
                eprintln!("Error: {}", e);
                process::exit(exitcode::IOERR);
            }
        }
    } else {
        match default_template::generate_files(output) {
            Ok(()) => {
                println!("Generated Digdag workflow files!");
                process::exit(exitcode::OK);
            }
            Err(e) => {
                eprintln!("Error: {}", e);
                process::exit(exitcode::IOERR);
            }
        }
    }
}
