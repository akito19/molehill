use std::env;
use std::process;
use molehill::generate_default_files;

extern crate exitcode;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() > 1 {
        panic!("This tool expects no argument.")
    }

    match generate_default_files() {
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
