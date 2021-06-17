use std::fs;
use std::io::{Write, Error};
use std::path::{Path, PathBuf};
use std::fs::File;
use std::vec::Vec;

struct Workflow<'a> {
    original_file_path: &'a PathBuf, // file path from the command-line argument.
    output: String,                  // output file path
}

pub fn generate_files(template: &str, output: &str) -> Result<(), Error> {
    let entries = get_entries(template).unwrap();

    for entry in entries {
        let file = &entry;
        let file_name = file.file_name().unwrap().to_str().unwrap();
        let wf_info = Workflow {
            original_file_path: &entry,
            // FIXME: Allow output path as `-o path/to/`
            //        Since this implementation allows only `-o path/to`
            output: output.to_string() + "/" + file_name,
        };

        generate(wf_info);
    }
    Ok(())
}

fn get_entries(template: &str) -> Result<Vec<PathBuf>, Error> {
    // TODO: Narrow down the number of extensions, just in case.
    //       Plan to enable directories and other extension files.
    // let extensions = [OsStr::new("dig"), OsStr::new("sql"), OsStr::new("py"), OsStr::new("html"), OsStr::new("txt")];
    let extensions = ["dig", "sql", "py", "html", "txt"];
    let dir = fs::read_dir(template)?;
    let mut entries: Vec<PathBuf> = Vec::new();

    for file in dir.into_iter() {
        let filepath = file?.path();
        if filepath.is_dir() {
            continue;
        } else {
            let ext = Path::new(filepath.file_name().unwrap()).extension().unwrap();
            if extensions.contains(&(ext.to_str().unwrap())) {
                entries.push(filepath);
            }
        }
    }
    Ok(entries)
}

fn generate(wf: Workflow) {
    let content = fs::read_to_string(wf.original_file_path).unwrap();
    let mut dest = File::create(wf.output).unwrap();
    write!(dest, "{}", content).unwrap();
    dest.flush().unwrap();
}

#[test]
#[allow(unused_must_use)]
fn valid_extension() {
    fs::create_dir_all("dir").unwrap();
    let mut file_dig = File::create("dir/foo.dig").unwrap();
    file_dig.write_all(b"echo>: hello").unwrap();

    let mut file_py = File::create("dir/foo.py").unwrap();
    file_py.write_all(b"printf('hello')").unwrap();

    let mut file_sql = File::create("dir/foo.sql").unwrap();
    file_sql.write_all(b"select * from users").unwrap();

    let mut file_html = File::create("dir/foo.html").unwrap();
    file_html.write_all(b"<div>hello</div>");

    let mut file_txt = File::create("dir/foo.txt").unwrap();
    file_txt.write_all(b"hello");

    let mut file_rb = File::create("dir/foo.rb").unwrap();
    file_rb.write_all(b"puts 'hello'");

    let entries = get_entries("dir").unwrap();
    assert_eq!(entries.len(), 5);

    fs::remove_dir_all("dir/").unwrap();
}
