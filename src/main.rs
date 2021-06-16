use std::env;

use molehill::generate_default_files;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() > 1 {
        panic!("This tool expects no argument.")
    }

    match generate_default_files() {
        Ok(()) => {
            println!("Generated Digdag workflow files!");
        }
        Err(e) => {
            println!("Error: {}", e);
        }
    }
}
